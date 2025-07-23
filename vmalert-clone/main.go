package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	_ "github.com/go-sql-driver/mysql"
	"gopkg.in/yaml.v3"
)

type Rule struct {
	Name        string `yaml:"name"`
	Description string `yaml:"description"`
	Query       string `yaml:"query"`
	Threshold   float64 `yaml:"threshold"`
	Condition   string `yaml:"condition"` // ">" or "<"
	Datasource  struct {
		Name string `yaml:"name"`
		URL  string `yaml:"url"`
	} `yaml:"datasource"`
	Export struct {
		Datastore string `yaml:"datastore"` // "mysql" or "file"
		File      struct {
			Path string `yaml:"path"`
		} `yaml:"file"`
		MySQL struct {
			Host     string `yaml:"host"`
			Database string `yaml:"database"`
			User     string `yaml:"user"`
			Password string `yaml:"password"`
		} `yaml:"mysql"`
		Action string `yaml:"action"`
	} `yaml:"export"`
}

type Config struct {
	Rules []Rule `yaml:"rules"`
}

type PrometheusResponse struct {
	Status string `json:"status"`
	Data   struct {
		ResultType string `json:"resultType"`
		Result     []struct {
			Metric map[string]string `json:"metric"`
			Value  []interface{}     `json:"value"`
		} `json:"result"`
	} `json:"data"`
}

func loadConfig(path string) (*Config, error) {
	data, err := ioutil.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var config Config
	err = yaml.Unmarshal(data, &config)
	return &config, err
}

func queryDatasource(rule Rule) (float64, error) {
	url := fmt.Sprintf("%s?query=%s", rule.Datasource.URL, strings.ReplaceAll(rule.Query, " ", "+"))
	resp, err := http.Get(url)
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return 0, fmt.Errorf("bad status code: %d", resp.StatusCode)
	}

	var promResp PrometheusResponse
	if err := json.NewDecoder(resp.Body).Decode(&promResp); err != nil {
		return 0, err
	}

	if len(promResp.Data.Result) == 0 {
		return 0, fmt.Errorf("no results")
	}

	valueStr := promResp.Data.Result[0].Value[1].(string)
	var value float64
	fmt.Sscanf(valueStr, "%f", &value)
	return value, nil
}

func exportToFile(rule Rule, value float64) error {
	alert := map[string]interface{}{
		"name":        rule.Name,
		"description": rule.Description,
		"value":       value,
		"timestamp":   time.Now().Format(time.RFC3339),
	}

	file, err := os.OpenFile(rule.Export.File.Path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer file.Close()

	enc := json.NewEncoder(file)
	return enc.Encode(alert)
}

func connectMySQL(rule Rule) (*sql.DB, error) {
	dsn := fmt.Sprintf("%s:%s@tcp(%s)/%s",
		rule.Export.MySQL.User,
		rule.Export.MySQL.Password,
		rule.Export.MySQL.Host,
		rule.Export.MySQL.Database,
	)

	var db *sql.DB
	var err error

	// Retry logic
	for i := 0; i < 5; i++ {
		db, err = sql.Open("mysql", dsn)
		if err == nil {
			err = db.Ping()
		}
		if err == nil {
			break
		}
		log.Printf("Retrying MySQL connection (%d/5): %v", i+1, err)
		time.Sleep(2 * time.Second)
	}
	return db, err
}

func exportToMySQL(rule Rule, value float64) error {
	db, err := connectMySQL(rule)
	if err != nil {
		return err
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS alerts (
		id INT AUTO_INCREMENT PRIMARY KEY,
		name VARCHAR(255),
		description TEXT,
		value DOUBLE,
		timestamp DATETIME
	)`)

	if err != nil {
		return err
	}

	_, err = db.Exec(`INSERT INTO alerts (name, description, value, timestamp) VALUES (?, ?, ?, ?)`,
		rule.Name, rule.Description, value, time.Now())
	return err
}

func evaluateRule(rule Rule) {
	value, err := queryDatasource(rule)
	if err != nil {
		log.Printf("Error querying datasource for rule %s: %v", rule.Name, err)
		return
	}

	triggered := false
	switch rule.Condition {
	case ">":
		triggered = value > rule.Threshold
	case "<":
		triggered = value < rule.Threshold
	default:
		log.Printf("Unknown condition for rule %s", rule.Name)
		return
	}

	if triggered {
		log.Printf("Rule triggered: %s - value: %f", rule.Name, value)
		switch rule.Export.Datastore {
		case "file":
			if err := exportToFile(rule, value); err != nil {
				log.Printf("Error exporting to file: %v", err)
			}
		case "mysql":
			if err := exportToMySQL(rule, value); err != nil {
				log.Printf("Error exporting to MySQL: %v", err)
			}
		}
	} else {
		log.Printf("Rule not triggered: %s - value: %f", rule.Name, value)
	}
}

func main() {
	config, err := loadConfig("rules.yaml")
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	for _, rule := range config.Rules {
		evaluateRule(rule)
	}
}

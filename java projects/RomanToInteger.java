import java.util.HashMap;
import java.util.Scanner;

public class RomanToInteger {
    public static int romanToInt(String str) {
        if (str  == null || str.length() == 0) {
            return 0;
        }

        // HashMap to store the values of Roman numerals
        HashMap<Character, Integer> rValues = new HashMap<>();
        rValues.put('I', 1);
        rValues.put('V', 5);
        rValues.put('X', 10);
        rValues.put('L', 50);
        rValues.put('C', 100);
        rValues.put('D', 500);
        rValues.put('M', 1000);

        int result = 0;

        for (int i = 0; i < str.length(); i++) {

            int presentValue = rValues.get(str.charAt(i));

            if (i < str.length() - 1 && rValues.get(str.charAt(i + 1)) > presentValue) {
                result -= presentValue;
            } else {
                result += presentValue;
            }
        }

        return result;
    }

    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);

        String romanNum = sc.nextLine().toUpperCase();
        int finalval = romanToInt(romanNum);
        System.out.println("Roman numeral " + romanNum + " is equivalent to " + finalval);
    }
}

import java.util.Scanner;

public class Pangram {
    public static boolean containsAllAlphabets(String sentence) {
        boolean[] alphabetPresent = new boolean[26];

        sentence = sentence.toLowerCase();

        for (int i = 0; i < sentence.length(); i++) {
            char cuval = sentence.charAt(i);

            if (cuval >= 'a' && cuval <= 'z') {
                alphabetPresent[cuval - 'a'] = true;
            }
        }

        for (boolean isPresent : alphabetPresent) {
            if (!isPresent) {
                return false;
            }
        }

        return true;
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter a sentence: ");
        String sentence = scanner.nextLine();

        if (containsAllAlphabets(sentence)) {
            System.out.println("The sentence is pangram");
        } else {
            System.out.println("The sentence is not pangram");
        }

        scanner.close();
    }
}

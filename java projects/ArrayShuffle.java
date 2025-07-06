import java.util.Arrays;
import java.util.Random;

public class ArrayShuffle {
    public static void main(String[] args) {
        int[] array1={1,2,3,4,5,6,7};

        Random rand = new Random();

        for (int i = 0; i < array1.length; i++) {
            int randindswap = rand.nextInt(array1.length);
            int temp = array1[randindswap];
            array1[randindswap] = array1[i];
            array1[i] = temp;
        }
        System.out.println(Arrays.toString(array1));
    }
}




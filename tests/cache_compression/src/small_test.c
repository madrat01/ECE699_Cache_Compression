#include <stdio.h>

#define ARRAY_SIZE 1000000
#define OFF 100

int main() {
    int arr[ARRAY_SIZE];
    int off = OFF;

    // Store similar values in adjacent addresses
    for (int i = 0; i < ARRAY_SIZE; i++) {
        arr[i] = i;
    }

    // Store different values in farther addresses
    for (int i = 0; i < ARRAY_SIZE / 2; i++) {
        arr[i] = i * 2 + OFF;
        arr[ARRAY_SIZE - i - 1] = i * 2 + 1;
    }

    // Print out the array values and their addresses
    //for (int i = 0; i < ARRAY_SIZE; i++) {
    //    printf("arr[%d] = %d (address: %p)\n", i, arr[i], &arr[i]);
    //}

    return 0;
}

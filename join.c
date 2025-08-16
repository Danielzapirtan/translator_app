#include <stdio.h>

int main(void) {
	while (!feof(stdin)) {
		int ch = getchar();
		if (ch != 10)
			putchar(ch);
	}
}


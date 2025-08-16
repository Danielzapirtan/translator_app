#include <stdio.h>

int main(void) {
	while (!feof(stdin)) {
		int ch = getchar();
		putchar(ch);
		if (ch == '.')
			putchar(10);
	}
}


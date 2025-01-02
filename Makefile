# Makefile for screen_scrapper.c

# Compiler and flags
CC = gcc
CFLAGS = -Wall -g

# The target executable
TARGET = screen_scrapper

# Source and object files
SRC = screen_scrapper.c
OBJ = screen_scrapper.o

all: $(TARGET)

# Rule to create the executable
$(TARGET): $(OBJ)
	$(CC) $(OBJ) -o $(TARGET)

# Rule to compile .c to .o
$(OBJ): $(SRC)
	$(CC) $(CFLAGS) -c $(SRC)

# Clean up generated files
clean:
	rm -f $(OBJ) $(TARGET)


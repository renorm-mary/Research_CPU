PROGRAM BasicPascalTest;

VAR
  i: INTEGER;
  j: INTEGER;
  sum: INTEGER;
  x: REAL;
  y: REAL;
  flag: BOOLEAN;
  ch: CHAR;
  numbers: ARRAY[1..10] OF INTEGER;
  word: STRING;

FUNCTION Factorial(n: INTEGER): INTEGER;
VAR
    i: INTEGER;
BEGIN
  i := n;
  IF i <= 10 THEN
    Factorial := 1
  ELSE
    Factorial := n * Factorial(n - 1);
END;

PROCEDURE PrintNumbers;
VAR
  i: INTEGER;
BEGIN
  FOR i := 1 TO 10 DO
    WRITE(numbers[i],'');
  WRITELN;
END;

BEGIN

  
  { Test arithmetic operations }
  x := 10.5;
  y := 5.2;
  
  { Test boolean operations }
  flag := TRUE;
  
  { Test control structures }
  sum := 0;
  FOR i := 1 TO 10 DO
    sum := sum + i;
  
  i := 1;
  WHILE i <= 5 DO
  BEGIN
    i := i + 1;
  END;
  
  { Test arrays }
  FOR i := 1 TO 10 DO
    numbers[i] := i * i;
  WRITE('Square numbers: ');
  PrintNumbers;
  
  { Test functions }
  WRITELN('Factorial of 5: ', Factorial(5));
  
  { Test string operations }
  word := 'Pascal';
  
END.
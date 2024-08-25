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


BEGIN

  
  { Test arithmetic operations }
  x := 10.5;
  y := 5.2;
  x:=10.87;
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
  
  { Test functions }
  
  { Test string operations }
  word := 'Pascal';
  
END.
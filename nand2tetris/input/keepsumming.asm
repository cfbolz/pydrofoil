(START)
@i 			// i refers to some RAM location
M=1 		// i=1
@sum 		// sum refers to some RAM location
M=0 		// sum=0
(LOOP)
	@i
	D=M 	// D = i
	@100
	D=D-A 	// D = i - 100
	@END
	D;JGT 	// If (i-100) > 0 goto END
	@i
	D=M 	// D = i
	@sum
	M=D+M 	// sum += i
	@i
	M=M+1 	// i++
	@LOOP
	0;JMP 	// Got LOOP
@START
0;JMP 		// Infinite loop

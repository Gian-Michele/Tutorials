**Screen**

Useful software to handle background launch of a program. Can be installed

	sudo apt-get install screen

Below the list of the most useful way to use scree

1.1)

	screen -S <NAME>  ./start.sh

Allow background launch of the script "start.sh", where < NAME > is the name to assign at the backgorund process. THe name will allow you to identify the program

1.2)

	screen -d -m -S <NAME>  ./start.sh

Same to 1.1 but allow you to goes back in the main terminal
1.3)

	screen -dmS -L <NAME> ./start

same command of 1.2 but is possible add Log of the background screen

2)

	screen -ls 

show you the list of all the programs launched with screen

3)

	screen -x <NAME>

Allow you to enter in the screen process with name <NAME>

4)

	screen -X -S <NAME> quit

Terminate the screen process with the name <NAME>  


Press the command Ctrl + a + d to exit from a process without terminate the process 
 

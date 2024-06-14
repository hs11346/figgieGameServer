# figgieGameServer

This is the Figgie Python Game Server built by Harry See. For rules about the game, please see the Jane Street webpage.

Files:
- app.py: The Flask server that hosts the endpoints 
- objects.py: The various abstractions for the game engine, including the deck and the orderbook
- clientGUI.py: A streamlit dashboard to play manually

Quick Start:
To play manually, run the app.py to start the server, then run the clientGUI.py by running "streamlit run clientGUI.py" in the command line.
Manual Game Instructions:
- In the second tab, there is text field for running commands
  - First, run "join,{your_name}" in the text field to initialise your user
  - When all players has joined, run "start"
  - To place a quote, run for example "quote,Diamonds,12,bid" to enter a quote, you will get a callback in the below box
  - To place a market order (trade), run for example "trade,Diamonds,buy"
  - When the game ends, you will see the results 
  - Then run "start" to start a new game
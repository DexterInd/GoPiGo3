
echo "ensuring only one instance of GoPiGo3 Scratch Communicator"
sudo pkill -f GoPiGo3Scratch.py
sudo python2 /home/pi/Dexter/GoPiGo3/Software/Scratch/GoPiGo3Scratch.py &

echo "starting Scratch"
scratch /home/pi/Dexter/lib/Dexter/Scratch_GUI/new.sb

echo "killing background process"
sudo pkill -f GoPiGo3Scratch.py
echo "background process killed"

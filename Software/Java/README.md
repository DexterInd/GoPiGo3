# JAVA INSTALLATION
There are a few things you need to do before you can run Java code on the GoPiGo3. 
If you've installed the latest version of Raspbian for Robots, you may skip this step. Verify that folder /opt/ contains the following folders: pi4j and json-simple. If they do not, follow this procedure.
Open up a command line on the GoPiGo3 and run the following commands:

```
cd ~/Dexter/GoPiGo3/Software/Java_new/main/java
sudo chmod +x *.sh
./install.sh
```

This will install all the needed jar files and do all of the necessary prep work. You should only have to do this step once.

# RUNNING PROGRAMS
Dexter Industries provides two scripts to allow for easy compilation of java programs on the GoPiGo3.
If you wish to run the demo, all you need to do is execute the run_demo.sh script. The robot will drive forwards a bit, turn around, and then drive in a arc before coming to a stop.

If you wish to run your own programs, simply make sure to add the following import statement:  
```import com.dexterindustries.gopigo3driver.*;```

Then, use your favorite file transfer service to transfer it to the GoPiGo. Place it in your directory of choice, and copy the run_file.sh script to the same directory.
Then, you just need to execute the run_file.sh script and pass the name of your file as an argument. Do not include the .java. 
For example, if your program is named Foo.java, the call should look like  
```./run_file.sh Foo```
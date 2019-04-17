# How to download Source Extractor

In root directory: <br>
`sudo apt-get update` <br>
`sudo apt-get install alien` <br>

In directory where you downloaded the 64-bit rpm from [here](https://www.astromatic.net/software/sextractor): <br>
`sudo alien -k sextractor-2.19.5-1.x86_64.rpm` <br>
`sudo dpkg -i sextractor_2.19.5-1_amd64.deb` <br>

______
OR, enter this line of code in terminal: <br>
`wget https://www.astromatic.net/download/sextractor/sextractor-2.19.5-1.x86_64.rpm && sudo apt-get install alien -y && sudo alien -i sextractor-2.19.5-1.x86_64.rpm`

To check if the installation worked, type this in any directory: <br>
`sex`<br>

Use bashrc to create an alias if you'd like to not type 'sex' every time you run source extractor.

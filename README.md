#RAMBo Uploader and Tester
This is the software we are developing for testing and programming RAMBo. 

#Usage
Run the tester with :

```sudo ./RAMBoTester.py```

You can also give it specific tests to run as arguments, for example :

```sudo ./RAMBoTester.py "Motors 1/16 Step" "Supply Voltages" "Mosfets Low"```

If you need to disable a test, you can currently do it programmaticaly in RAMBoTester.py by editing the file and adding a line similar to :

```r.GetTest("Program Vendor Firmware").enabled = False```

#License
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
You should have received a copy of the GNU General Public License along with this program. If not, see [http://www.gnu.org/licenses/].

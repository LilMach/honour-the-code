# honour-the-code

Welcome to our GitHub repository for our form filler program. A few things to note:
- The lambdafunctioncode.py is just the python code used by the lambda function and should not be run by the IDE. This code is run by the AWS in a lambda function, which is then called by our program.
- Since we are using AWS to run the program, access keys to an IAM user is needed so that the program can access the S3 bucket that stores the files. In this file (FormFiller.py) you will see that those lines of code have been left blank for security reasons. This means that the program will not run as intended if you do not have access to the access keys. We cannot include the security keys because people will be able to keep calling the function and charge the AWS account.
- Please contact us for the access keys if you wish to run this program for yourself.
 
Contact details: 
Name - Aditya Jain
Phone number - 0412944008 
Email - jainaditya1704@gmail.com

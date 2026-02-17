
# cybersecurity-labs

<h3>Using Hydra to Crack Passwords</h3>

<p>1. In a controlled lab environment in Labex, I used several basic login attempts to understand how an authentication page responds to an input. Since these inputs are incorrect, the message was a generic "Invalid Username or Password!"</p>

<img width="506" height="467" alt="Screenshot 2026-02-17 151406" src="https://github.com/user-attachments/assets/d89c03cc-042d-4fb6-a994-9e5178f7ae51" />

<p>I understood that by using the word "or" and very vague and generic phrases, the page doesn't tell you if the username exists or if the password is the one that is incorrect. And its really cool to know that this is actually a self explanatory concept called "Security through obscurity"!</p>

<p>I also learnt that captchas, account lockouts and various other security authenticators exist so that attackers can not automate any of these tasks. And what I did just now is actually a type of manual brute force attack! In fact attackers use thousands of credentials to sift through quickly and they use lists of most common passwords, and that is why weak password combinations are strongly discouraged. And those password requirement protocols exist for a reason!</p>

<p>2. Now its time to dive deep and see what is a pre-compiled password list file and how it helps in a brute force automation. So for this step, I downloaded a list of common passwords that I found over the internet at this location: /home/labex/project/500-worst-passwords.txt</p>

<p>And then I opened up my terminal and read out the first 10 lines of the file using the "head" command: head -n 10 500-worst-passwords.txt</p>

<img width="1229" height="841" alt="image" src="https://github.com/user-attachments/assets/3e87cb6b-34bf-4723-827e-c2bd7230340a" />

<p>In cybersecurity, these types of brute force attacks are more specifically called "Dictionary Attacks", because instead of using all possible password combinations, attackers use known passwords first to significantly improve their chance of gaining access. And its true that simple passwords like these are the go-to password for millions of people worldwide.</p>

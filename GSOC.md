
<p align="center"><img height="250px" src="https://1.bp.blogspot.com/-8g85F6YR8r0/WpcCNxJM_sI/AAAAAAAABbc/tpLh1if0MgYS3l1vqaEMwLPAaxC_nv81QCLcBGAs/s1600/GSoC%2B-%2BVertical%2BWide%2B-%2BGray%2BText%2B-%2BWhite%2BBG.png"></p>

# Hephaestus: Testing the TypeScript Compiler

## A project outline by [Alex Papadopoulos](https://www.linkedin.com/in/alexios-papadopoulos-siountris-855935240/)

Organisation: [GFOSS - Open Technology Alliance](https://github.com/eellak/)

Central Repository: [Hephaestus](https://github.com/hephaestus-compiler-project/hephaestus)

Mentor: [Thodoris Sotiropoulos](https://github.com/theosotr)

## 📚 Contents

- Project Description
- Communicating with the Hephaestus Team
- Development Outline
  - Git/GitHub: Branch and Repo Management
  - Important Features
  - Automated Testing
- Pull Request Overview
- Results
- What's next?

## 💭 Project Description

Hephaestus is a compiler testing tool, designed to test the compilers of statically-typed languages. Namely, upon the start of the GSoC '22 cycle, Hephaestus was actively testing and had found bugs in the languages of Java, Kotlin, and Groovy.

My task was to expand Hephaestus to test and find bugs in the compiler of TypeScript, a language by Microsoft that has risen in popularity in the previous decade.

Below we will go over important moments that shaped my GSoC project, with the aim of describing the development process and providing useful tips for future GSoC contributors.

## 📧 Communicating with the Hephaestus Team

Communication with your mentor during GSoC is crucial. Mentors can make or break a GSoC project and, in my case, I was paired with a great one. Thodoris motivated me and guided me through blockers, head scratchers, and problems that all contributors will eventually face in one way or another.

Hephaestus is housed at a research lab, so I was lucky to have the ability to meet up and work with Thodoris on-site at the lab. At the same time, we also held virtual meetings whenever needed.

Both virtually and on-site we had pair programming sessions when needed. Whenever I stumbled upon a problem that I could not solve by myself, after going through all other avenues (properly searching the internet, writing unit tests, using the python debugger etc.) we sat down together and tried to fix the problem. Those sessions were extremely helpful and I learnt a lot both from being the one coding, but also from being the one discussing the problem while Thodoris typed our solution out.

Pair programming is a very important skill for any developer team out there. A make-or-break tip for these sessions (especially for Junior Developers) is to go into them prepared. First exhaust all other possible means (in a reasonable time-frame) and be able to tell the other person what you have already tried. This way, no time is wasted and you can more effectively crack the problem.

Thodoris and I used a [Slack](https://slack.com/) group to communicate throughout the program both for coordinating our efforts but also for updating other Hephaestus team members with my progress.

## 👨‍💻 Development Outline

### Git/GitHub: Branch and Repo Management

By participating in the Google Summer of Code program, I learnt how to seamlessly integrate Git and GitHub in my workflow when working with large projects. From rebasing branches to using handy commands like [git-bisect](https://git-scm.com/docs/git-bisect), I can now easily navigate and contribute to larger codebases, while utilizing tools that are vital to all developers regardless of their field.

This was the first time I used Git outside of personal or small-team projects, which equipped me with necessary skills for any future project.

### Important Features

Lots was added, discarded, and rewritten during GSoC '22 for the Hephaestus project. Which features were the most challenging and important?

- **Translating an Abstract Syntax Tree (AST) to TypeScript**

The first feature I completed was perhaps the one with the biggest learning curve. While future additions were in fact more complex, the first one was the most all-around challenging.

It is not hard to think of why. I had to deeply understand the functionality of an AST as well as how the mechanisms of Hephaestus cooperated to produce the tree itself. Aside from the learning material directly related to this feature, I also had to get a good understanding of properly contributing in Open Source as a whole before I could even start coding this out.

- **Making Hephaestus extensible**

It turns out that trying to add a language with exclusive features to a language agnostic compiler tester comes with its challenges.

The applications and handling of certain cases in the core generator were not designed with TypeScript features in mind (eg. Union Types).

As a result, I had to find a proper and effective way for one to extend the core generator of Hephaestus to features that are language-specific. After designing this with my mentor, we proceeded with its application.

Now, everyone can extend Hephaestus to any language they want, and there already is a way to add language-specific features without changing the core and language-agnostic nature of Hephaestus.

### Automated Testing

Automated Testing is important for all healthy codebases. After a certain point, the code changes are too many to keep manually testing features. One must know at any point if an addition broke some part of the code, in order to quickly and effectively act upon that information to fix potential bugs.

Throughout GSoC, I wrote a number of unit tests to ensure stability, increase code coverage, and fix bugs.

## 🌿 Pull Requests

<table>
<thead>
<tr>
<th>Status</th>
<th>Name</th>
<th>Diff</th>
</tr>
</thead>
<tbody>
<tr>
<td>✅</td>
<td><a href = "https://github.com/alexisthedev/hephaestus/pull/1">TypeScript Translator</a></td>
<td><font color ='green'>+1020 <font color ='red'>−530</td>
</tr>
<tr>
<td>✅</td>
<td><a href = "https://github.com/alexisthedev/hephaestus/pull/3">Null and Undefined types. Null Constant</a></td>
<td><font color ='green'>+88 <font color ='red'>-7</td>
</tr>
<tr>
<td>✅</td>
<td><a href = "https://github.com/alexisthedev/hephaestus/pull/12">Literal Types</a></td>
<td><font color ='green'>+155 <font color ='red'>−11</td>
</tr>
<tr>
<td>✅</td>
<td><a href = "https://github.com/alexisthedev/hephaestus/pull/13">Type Aliases</a></td>
<td><font color ='green'>+307 <font color ='red'>-111</td>
</tr>
<tr>
<td>🚧</td>
<td><a href = "https://github.com/alexisthedev/hephaestus/pull/14">Union Types</a></td>
<td><font color ='green'>+471 <font color ='red'>−77</td>
</tr>
</tbody>
</table>

## Results & What's Next

After the GSoC program, I am now a member of the research lab that houses the Hephaestus project: the [AUEB BALAB](https://www.balab.aueb.gr/)!

I will stay on the Hephaestus team and contribute to the project. I am very excited for the future to come.

Thanks to my mentor Thodoris, the BALAB team, and all the GSoC community members that made this summer one to remember!

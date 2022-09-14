# hardInfo

The purpose of this project is to create a Python API for gethering personal computer hardware information and other platform information into usable objects insode a Python program.  The general method it employs is to safely run Linux commands from within Python and then parse the output.

Writing Python programs to run on any operating system on any hardware is not possible without being able to dynamically adapt to the stack of layers running beneath your program.  Although Python's library is very helpful in this regard, there are still problems adapting various functional categories of features, such as those required for security and forensic progamming, so that the result is as general as possible.  This project aims to solve that by collecting anything and everything relevant, thereby also providing a general interface to Linux commands usable in any Python program.

An interesting possible spin-off once all the hardware and other low level components are represented by objects is to implement the behavior of each as stated in their standaards using methods defined in their respective classes, and then to run the component system in real time in parallel with the actual computer hardware and software stack by receiving real-time event messages from it.  The system state can then be compared to the model state to detect any malfunctions or malware produced anomalies.

Module Ownership:

I think the best approach to developing software together is for each of us to take ownership of a module which addresses a high level development issue and to be responsible throughout development for that module or modules. Each of us can then code according to his or her own principles and only needs to understand the other programmers' enough to interface with the modules that theirs depend on or that depend on theirs. The only qualifier to actual ownership of the intellectual property rights in the module your responsible for is that your have agreed to allow it to be used in the application under development under whatever licensing scheme is settled on by the developers. My preference is a "freemium" model, where there is a free community edition and a paid for commercial or professional one or more building directly off of the free version.


Architecture:

The concept of decoupling of software components and its advantages extends far beyond the Model-View-Controller architecture level to potentially all of the classes or entities which are designed for a particular information processing solution.

The Model-View-Controller architectures promoted by Sun Microsystems for use with its Java programming language is well known in the software development industry. Its emphasis is on decoupling the data from the user interface and both from the business logic control so that each can be reused with different components. The concept of decoupling of software components and its advantages extends far beyond this general architectural level to potentially all of the classes or entities which are designed for a particular information processing solution. The example I will use to demonstrate the principles and their advantages is a simulation of an automobile steering system. The entities or classes involved include the steering wheel, the steering column, the rack and pinion box, and the tie rods connecting the steering gears to the wheels. My basic decoupled solution is illustrated in the UML diagram included below.

Procedural code with record structures for each of these entities would require at minimum the ability to reference any other entity that it needs to access or control. This depends on the execution scope, so the reference need not be embedded if it is available otherwise in the execution scope. This implies being available to anything operating in that scope, however.

Object oriented code has the same problem. For the steering wheel to control the steering column, it must either have as an attribute a reference to the steering column to be able to call its methods with its own, or have a reference to it passed in as an argument of the method that will access the other object or invoke one of its behaviors. Conceptually, the steering column is not really a part or attribute of the steering wheel, so the first option is already a violation of the basic rules of class design. Passing a reference in from the current execution scope is the only consistent option. With respect to scope and visibility, this is nearly identical to procedural code except that it adds the feature of privacy to those attributes and functions that do not need visibility outside of the particular entity.

In addition, for security, an object oriented language must be strongly typed. When you pass a reference to one entity into a method of another, its type must be declared and is checked automatically. In the case of the steering column, for full strength security the reference can only refer to a particular class of steering column. You could design a steering column base class and for any particular type derive from it, declaring the parameter to be of the base class type, but then any of a hundred different derived types could be passed in and your steering wheel code must test the type to know how to control it. To do this, it could use a language feature called reflection, which allows program access to the meta data describing any object’s design, including its methods, attributes, access rights, etc. This is inherently a potential virus attack window which can be used to at minimum record the internal controlling attributes of a program’s classes.

This exposure is the direct result of the tight, type strict coupling between cooperating entities required in a conventional OOP program designed according to standard architectural principles and patterns. The more general and reusable you want the code to be, the more variability you must add to the entities through derivation from common base classes to particular instance instantiating ones. If you want to model any steering system with the best security, you have to particularize your entities and are then forced to rewrite the code for any variation.

Assuming a standard steering column method and behavior dictionary applicable in all steering column classes, which a general Java interface would accomplish, you can skip type testing and return false from the implementations of the methods which are not relevant to a particular class. This complicates your controller code considerably, requiring understanding of the inner workings of the controlled entity from the one accessing its methods. This is yet another type of coupling, binding each cooperating entity to a particular interface definition which it must navigate the logic of to make meaningful use of it. With standard design methods, there is no secure way out of this complexity.

The common interface does achieve a respectable level of generality, if not full decoupling, but there is a much more decoupled, general, simple, and flexible approach. By “decoupled”, I mean that you can potentially fit any steering wheel to any steering column, any steering column to any rack and pinion steering controller design, and so on. Along with this generality, full decoupling also provides the best security because the communication surface area between entities is minimized without need for type generality or use of reflection.

The means of accomplishing full decoupling is messaging. Each class has a method dedicated to receiving messages from any other object of any other class. This message receiver has as its sole argument a single, strongly typed, arbitrary map of attributes. A map is simply a list of name-value pairs, just like the attributes of an object. A reference to this method is passed to an object during its construction as a “listener”, which the object can then use to send messages to the listening object. Invoking listener( message ) with a map of attributes invokes the receiver’s messageReceiver( message ) method passing it the arguments listed in the map. Each entity or object can then send instructions or reports to any other for which it has a recorded listener. The message receiver can have any name, and the only execution scope issue is that there must be a reference to the receiving object in the scope in which the sending object’s constructor is called for the messageReceiver() reference to be passed to it.

Using this architectural paradigm, no object, class, entity or part has to embed any information regarding any other component other than a reference to its message receiver. Also, the execution scope no longer needs to have all cooperating components referenced in it for them to work together however the user desires. You could also implement a centralized message routing class so that only names of the destination entity instances, as registered in the manager, need to be recorded in message sending entities. Design of such a communications manager is beyond the scope of this article, however even without it, you can securely send any commands or instructions or updates from any component to any other, along with reports back respecting the effect of acting on them.

The ingenuity of the programmer is the only limit respecting how to act on particular messages, and designs can be communicated to the user with a standard message dictionary for a particular application. With direct messaging, the steering wheel sends messages to the steering column telling it its movements in sufficiently detailed time increments for effective response. The steering column passes its response behavior reports both to the rack and pinion mechanism and back to the steering wheel, and so on.

The most significant security advantage of complete decoupling is that all methods which can change the state of the object, meaning the values of its fields, are now protected or private rather than public, along with all of the attributes themselves. They can be invoked exclusively by the method that receives messages from other objects. Using this completely decoupled architecture, only one method, the messageReceiver(), needs to be public in any class. All components can be standard and reusable and the applications using them are much more secure than with standard software application development patterns, principles, and architectures. Messaging accomplishes all of this intuitively.

If you would like to support this project, you can contribute here:
https://www.buymeacoffee.com/keithmichah


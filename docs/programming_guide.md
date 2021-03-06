#### 缓存计算结果

常规顺序数据分析应用设计
1. 采用常规基于编写的程序有几点好处：代码采用同步的方式编写，调式起来难度相对较小；
   思路也较为容易理解。
2. 为什么要将处理器间传递的数据进一步包装，而不是传递纯的带计算的数据？
   简单计算函数，它们的参数均需要通过函数入口传递，函数是无状态的，传递正确的可以
   计算的类型就可以，如求和函数输入数值型数据就可以计算了，不论何种函数都是这样的；
   即便是通常的OOP编程也是这样的，只要传入的数据类型对就可以计算。但是这样有时候
   不能满足需求，对某些数据进行计算是需要一定的前提参数的，不仅仅要知道数据的类型，
   还需要更对关于这条数据的其他的信息，也即是关于数据的数据(元数据)，根据这些先验
   选择调整合适的前提参数(动态获取或者动态调整)，进而才能完成合适的数据计算。这是
   设计更复杂的数据处理器输入参数类型的原因，该参数类型会影响到处理器的状态，也即
   根据数据输入动态的影响处理器，进而影响其行为；还有更狠的是动态的影响程序的逻辑，
   不仅仅是参数。当然对于简单的程序可能无此复杂抽象的必要。
3. 对每个处理器配备缓存，缓存实现方式，装饰器，或者是Hooker或者handler类的方法等，
   不关怎样这些都要提供对外的一致性接口以便调用，不然依赖其的上层不能进行稳定抽象。
4. 为什么不使用一个第三方对象来维护所有的处理器的附加功能？<1> 全局对象的影响是全
   局的，修改带来的影响也是全局的，是不是该避免这种对象存在。<2> 各种处理的需求是
   多样性的，经常需要改变或者增加，这对导致，第三方公共类的变动，这样的话抽象第三
   方的意义会减弱，若第三方出问题会全部不能使用，具有全局性耦合，因此把影响控制在
   局部，可以方便控制。<3> 有时候有的处理器需要某种功能而有的又不需要，难以用第三
   方同调，而且第三方需要了解关于处理器更多。   
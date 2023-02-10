from experta import *


class BaseIndividual(object):
    '''
    其实这个也可以被替换掉，因为我只要在BaseConcept class给一个叫self.value的属性，那么这个属性有值的时候，它就是一个individual。为空时表示整个concept
    这样就等价于目前的处理方法。这样只是能强化一下对AL的印象hhh，但是写得繁琐一点。这你们随缘叭，反正按道理怎么选都行。
    '''

    def __init__(self, value, name, comments='null'):
        self.value = value  # 值
        self.comments = comments  # 注释
        self.name = name  # 个体的类型名，不过这个也可以直接注释掉，反正都自动化了。注释掉反而更不容易出错hhh

    def __eq__(self, other):
        return type(self) is type(other) and self.value == other.value

    def __hash__(self):
        return (self.value, type(self))


class BaseConcept(object):

    def __init__(self, name, comments='null'):
        self.name = name  # 概念名/概念类型
        self.comments = comments  # 注释
        # self.unary_ops = [] #一元算子，即私有属性

    def __eq__(self, other):
        return type(self) is type(other)

    def __hash__(self):
        return type(self)
    # def __hash__(self):
    #     return self.mro()[-2]

    # def check_scope(self, InputVariable):
    #     if isinstance(InputVariable, BaseIndividual):
    #         pass
    #     elif isinstance(InputVariable, BaseConcept):
    #         pass
    #     elif isinstance(InputVariable, Term):
    #         pass
    #     elif isinstance(InputVariable, Assertion):
    #         pass #我还没实地见过
    #     else:
    #         pass


class BaseOperator(object):
    def __init__(self, name, variables_name, inputType=None, outputType=None, outputName=None, func=None,
                 comments='null'):
        self.variables_name = variables_name
        self.inputType = inputType
        assert len(self.variables_name) == len(self.inputType)
        self.outputType = outputType
        self.func = func
        self.outputName = outputName
        self.comments = comments
        self.name = name

    def __call__(self, variables):
        '''
        理论上应该是你之前实现的，调用数据库的方案
        简便起见，我这里就认为Individual是简单的tuple了
        '''
        if self.func == None:
            return None
        else:
            return self.func(*variables)


class Term(object):
    '''
    我们在这里约定，仅认为op(c1,c2...)是term，而不遵循常规的term定义。因为目前没啥必要，而且影响if语句的简洁
    '''

    def __init__(self, operator='null', variables='null', comments=''):
        self.operator = operator  # BaseOperator
        self.comments = comments
        self.variables = variables
        #print('|||')
        #print(len(self.operator.variables_name))
        #print(len(self.variables))
        if not operator == 'null' and not operator == None:
            assert len(self.variables) == len(self.operator.variables_name)
            self.variables = list(self.variables)
            for pos, (variable, v_type) in enumerate(zip(self.variables, self.operator.inputType)):
                # 如果是用的python内置的数值类型，而不是concept，则自动转化
                if type(variable) in [str, int, float, list, tuple, dict]:
                    class_name = v_type.name[:len(v_type.name) - len('Concept')] + 'Individual'
                    individual_var = eval(class_name)(variable, class_name)
                    # 默认InputType都用的是concept而不是individual
                    self.variables[pos] = individual_var

            for variable, v_type in zip(self.variables, self.operator.inputType):
                #print(variable)
                #print(v_type)
                if not check_scope(variable, v_type):
                    assert 1 == 0
                # if isinstance(variable, type): #type都是concept
                #     assert type in type(variable).mro() #继承关系
                # else:
            self.variables = tuple(self.variables)

    # def __eq__(self, other):
    #     return type(self) is type(other) and self.operator == other.operator and self.variables == other.variables
    #     #这里就不支持运算后相等了，比如add(2,2)和4认为不相等，想要相等，等运算结果的吧。我不是很确定这会不会带来一定的问题，目测还好
    #
    # def __hash__(self):

    def GetFinalVariables(self, variables):
        new_variable = []
        for variable in variables:
            if isinstance(variable, Term):  # 先不考虑assertion
                tmp = variable.operator(self.GetFinalVariables(variable.variables))
                if isinstance(tmp, list):
                    new_variable.extend(tmp)
                else:
                    new_variable.append(tmp)
            else:
                new_variable.append(variable)
        return tuple(new_variable)

    def GetRHS(self):
        print(self.variables)
        return self.operator(self.GetFinalVariables(self.variables))  # 返回None的时候代表着不可执行，有可能会用到这个判断


class Assertion(Fact):
    def __init__(self, LHS='null', RHS='null', comments='null'):
        super(Fact).__init__()
        self.LHS = LHS
        self.RHS = RHS

        if not self.LHS == 'null' and not isinstance(self.LHS, W):  # 不排除第二个判断在其他地方有遗漏
            assert isinstance(self.LHS, Term) or isinstance(self.LHS, W)  # 这个约束也是非常规的，不过...别的形式目前也没啥用
        if not self.RHS == 'null' and not isinstance(self.RHS, W):
            assert not self.LHS == 'null' and not isinstance(self.LHS,
                                                             W)  # 给了这个约束是在于，就算是W()，那一个不提供operator的Assertion也是没意义的
            # 我充其量询问，我啥时候在上海读得书啊？，上海是RHS。但不可能问，我的哪些信息是和上海有关的（或者说我的哪些算子的RHS是上海，这个通常没有意义）

            # 如果是用的python内置的数值类型，而不是concept，则自动转化
            if type(self.RHS) in [str, int, float, list, tuple, dict]:
                v_type = self.LHS.operator.outputType
                class_name = v_type.name[:len(v_type.name) - len('Concept')] + 'Individual'
                individual_var = eval(class_name)(self.RHS, class_name)
                # 默认InputType都用的是concept而不是individual
                self.RHS = individual_var

            assert check_scope(self.RHS, LHS.operator.outputType)  # in type().mro()
            assert isinstance(self.RHS, BaseConcept) or isinstance(self.RHS, BaseIndividual) or isinstance(self.RHS,
                                                                                                           Term)

        self.update(self.GetHash())
        self.comments = comments

    def GetRHS(self):
        if self.RHS == 'null':
            return self.LHS.GetRHS()
        else:
            return self.RHS

    def GetHash(self):
        var_dict = {}
        if not self.LHS == 'null':
            for var, var_name in zip(self.LHS.variables, self.LHS.operator.variables_name):
                if not isinstance(var, Term):  # 这里是错的
                    var_dict[var_name] = var.value
            # var_dict[self.LHS.operator.outputName] = self.RHS.value#.value #得要的
            var_dict['opeator'] = self.LHS.operator
        return Fact(**var_dict)  #

    def __eq__(self, other):
        return type(self) is type(other) and self.GetHash() == other.GetHash()

    def __hash__(self):
        if type(self.RHS) == str:
            print('hash', self.RHS, self.GetHash().__hash__())
        else:
            print('hash', self.RHS.value, self.GetHash().__hash__())
        return self.GetHash().__hash__()


class Exist(Fact):
    pass


class Tmp(Fact):
    '''
    为了写着舒服，单独开一个过渡
    '''
    pass


# 汇率↓ → 需求↑ → 价格↓。时间我只考虑future和now这两种取值，不过...这个大概率是要调整的，但是得根据各自数据的情况，我们最终商定一个方案。
def create_individual_concept(class_name, parent_classes='Base', val_dict={}):
    '''
    :param class_name: 新类的名字
    :param parent_classes: 要继承的类，默认Base
    :param val_dict: emm...我暂时没有用途，先留着。
    :return: individual和concept的类
    '''
    individual_class = None
    concept_class = None
    if parent_classes == 'Base' or parent_classes == None:
        individual_class = type(class_name, (BaseIndividual,), {'name': class_name + 'Individual', **val_dict})
        concept_class = type(class_name, (BaseConcept,), {'name': class_name + 'Concept', **val_dict})
    else:
        individual_class = type(class_name, parent_classes, {'name': class_name + 'Individual', **val_dict})
        concept_class = type(class_name, parent_classes, {'name': class_name + 'Concept', **val_dict})
    return individual_class, concept_class


Fake_database = {'raw_petroleum': {},
                 ('RMB', 'dollar', 'future', '1'): 7,
                 ('RMB', 'dollar', 'now', '1'): 8, }

NumberIndividual, NumberConcept = create_individual_concept('Number', 'Base')
VarcharIndividual, VarcharConcept = create_individual_concept('Varchar', 'Base')
DateIndividual, DateConcept = create_individual_concept('Date', 'Base')
CurrencyIndividual, CurrencyConcept = create_individual_concept('Currency', 'Base')
GOODIndividual, GOODConcept = create_individual_concept('GOOD', 'Base')
IndustryClassIndividual, IndustryClassConcept = create_individual_concept('IndustryClass', 'Base')
# 不过没啥复用需求的，用str,int之类的就也蛮好，只是需要改check scope里的判断。主要是因为，用其他推理引擎的话，我们倒也没必要考虑私有不私有了


GetExchangerateOperator = BaseOperator(name='GetExchangerateOperator',
                                       variables_name=['ICurrency', 'OCurrency', 'DATE', 'PriceType'],
                                       # 大小写有些不统一hhh，你们看着决定吧
                                       inputType=[CurrencyConcept, CurrencyConcept, DateConcept, NumberConcept],
                                       outputType=NumberConcept,  # NumberConcept更好看一点，换成NumberIndividual是更稳一点，都行都行
                                       outputName='Exchangerate',
                                       func=lambda x, y, z, a: Fake_database[(x.value, y.value, z.value, a.value)])

MinusOperator = BaseOperator(name='MinusOperator',
                             variables_name=['Minuend', 'Subtrahend'],
                             inputType=[NumberConcept, NumberConcept],
                             outputType=NumberConcept,
                             outputName='MinusResult',
                             func=lambda x, y: x.GetRHS - y.GetRHS if isinstance(x, Term) else x - y)

GetDemandOperator = BaseOperator(name='GetDemandOperator',
                                 variables_name=['GOOD', 'DATE'],
                                 inputType=[GOODConcept, DateConcept],
                                 outputType=NumberConcept,
                                 outputName='DEMAND',
                                 func=None)  # 这个我的样例中反正用不到，我就随便了啊，按理是有func的


# class NumberIndividual(BaseIndividual):
#     def __init__(self):
#         super(BaseIndividual).__init__()
#         self.name = 'NumberIndividual'
#
# class NumberConcept(BaseConcept):
#     def __init__(self):
#         super(BaseConcept).__init__()
#         self.name = 'NumberConcept'
#
# class DateIndividual(BaseIndividual):
#     def __init__(self):
#         super(BaseIndividual).__init__()
#         self.name = 'DateIndividual'

def check_scope(InputVariables, Scopes):
    '''
    为了简单起见，这个函数尽量只用于匹配concept角度是否正确，而不用于匹配具体individual的值是否一模一样。虽然确实提供了简单的匹配值的能力。
    复杂的值匹配靠schema处理吧，我尽量试着绕开重复造轮子的情况
    '''

    def check_single_input(InputVariable, Scope):
        if Scope == 'ANY':
            return True

        # if isinstance(InputVariable, Scope):
        #     return InputVariable==Scope
        # else:
        #     if isinstance(BaseIndividual, InputVariable) and
        if isinstance(InputVariable, BaseIndividual):
            if isinstance(Scope, BaseIndividual):
                return InputVariable == Scope
            else:
                match = Scope  # 这一行目前成无意义的了。BaseConcept正常匹配
                if Scope is Term:  # Scope非要用Term的情况，应该只有占位符。我们暂时取消了所有的占位符，所以我就不写这个了。留个提醒
                    print("碰到再说")
                    pass

                return eval(InputVariable.name[:len(InputVariable.name) - len('Individual')] + 'Concept') in match.mro()

        elif isinstance(InputVariable, BaseConcept):
            if Scope is BaseIndividual:
                return False

            match = Scope  # 这一行目前成无意义的了。 BaseConcept正常匹配
            if Scope is Term:  # Scope非要用Term的情况，应该只有占位符。我们暂时取消了所有的占位符，所以我就不写这个了。留个提醒
                print("碰到再说")
                pass

            return type(InputVariable) in type(match).mro()

        elif isinstance(InputVariable, Term):  # 我最近的建模中把占位符去掉了，这个情况理论上是会被规避掉的。只保留做个提醒，或许日后需要
            if Scope is BaseIndividual:
                return False

            match = Scope  # 这一行目前成无意义的了。BaseConcept正常匹配
            if Scope is Term:  # Scope非要用Term的情况，应该只有占位符。我们暂时取消了所有的占位符，所以我就不写这个了。留个提醒
                print("碰到再说")
                pass

            return InputVariable.operator.outputType in match.mro()

        elif isinstance(InputVariable, Assertion):
            print("碰到再说")  # 我还没实地见过
        else:
            return False

    if not isinstance(Scopes, list):
        InputVariables = [InputVariables]
        Scopes = [Scopes]

    assert len(InputVariables) == len(Scopes)

    for InputVariable, Scope in zip(InputVariables, Scopes):
        if isinstance(Scope, list):
            if sum([check_single_input(InputVariable, s) for s in Scope]) == 0:  # 有一个对了就行
                return False
        else:
            if not check_single_input(InputVariable, Scope):
                return False
    return True


from experta import *


class OurSystem(KnowledgeEngine):  # GetExchangerateOperator
    @DefFacts()
    def SetDefault(self):
        yield Exist(test='test')

    # 此条规则是：我们所用货币对美元的汇率如果增加，说明购买力增加，然后会导致石油(仅石油，比如天然气可能不遵循这个规律)的需求增加
    @Rule(Exist(test='test'),  # 无用
          Exist(GOOD=MATCH.GOOD, BEGIN=MATCH.BEGIN, END=MATCH.END),  # !!!注意MATCH这是从左向右赋值，而不是正常的右向左
          Exist(ICurrency=MATCH.ICurrency, OCurrency=MATCH.OCurrency, PriceType=MATCH.PriceType),
          TEST(lambda OCurrency: OCurrency == 'dollar'),
          # 这里需要约定一个事情，就是什么样的信息一起出现。你比方说这里我默认的是，
          # 所有商品我都只关注这些背景信息(如我使用的货币都是人民币)的前提下，我想求石油在未来的情况。这样的话我就不能针对不同的货物关注不同的货币。
          # 或者严谨来说是如果我放了很多货币的话，他会对所有的货物都值钱，我设置的所有货币，而不是说单对单的。
          # 这样的好处在于我可以统一给一些值设一个空值等缺省值(当然我这里面没有干)。如果想追求单对单的话，那就需要。在输入的事实的时候，分别把每一个参数都给定它，
          # 或者手写一个函数自动补全掉那些缺省值，都行都行。
          # MATCH.BeginRate << Tmp(val=Term(operator=GetExchangerateOperator, variables=(OCurrency, ICurrency, BEGIN, PriceType))),
          # MATCH.EndRate << Tmp(val=Term(operator=GetExchangerateOperator, variables=(OCurrency, ICurrency, END, PriceType))),

          TEST(lambda ICurrency, OCurrency, BEGIN, END, PriceType:
               Assertion(Term(operator=MinusOperator,
                              variables=(Term(operator=GetExchangerateOperator,
                                              variables=(ICurrency, OCurrency, BEGIN, PriceType)),
                                         Term(operator=GetExchangerateOperator,
                                              variables=(ICurrency, OCurrency, END, PriceType)))),
                         RHS='null').GetRHS() > 0))  # 我想了很久，都没想到能在这里设置临时变量的办法，开全局变量似乎能以非常繁琐的方式做到但不值得。
    # 所以这里就显得很长很长...你们要是想到了什么办法就教教我呗

    # Term(operator=GetExchangerateOperator, variables1=MATCH.variables), #(ICurrency=~L('dollar'), OCurrency1='', DATE1=MATCH.DATE, PriceType1=MATCH.PriceType)
    #   Term(operator2=MATCH.operator, variables2=MATCH.variables) #(ICurrency=~L('dollar'), OCurrency2=MATCH.OCurrency, DATE2=MATCH.DATE, PriceType2=MATCH.PriceType)
    #   [],
    #   TEST())
    def E2D(self, GOOD, ICurrency, OCurrency, BEGIN, END, PriceType):
        print("触发规则1：汇率↓ → 需求↑")
        #print(ICurrency)
        #print(type(ICurrency))
        BeginRate = Term(operator=GetExchangerateOperator, variables=(ICurrency, OCurrency, BEGIN, PriceType)).GetRHS()
        EndRate = Term(operator=GetExchangerateOperator, variables=(ICurrency, OCurrency, END, PriceType)).GetRHS()
        print("从{}到{}的时间里，预期{}兑换{}的汇率将由{}下降到{}".format(BEGIN, END, OCurrency, ICurrency, BeginRate, EndRate))
        EndDemand = 8
        BeginDemand = 7  # 这里就是随便赋值了，正常是通过相关函数计算的
        # 如果没有，则给出的是"promote"这样的标签，或者其他能满足需求的表示方案。这些根据实际情况随机应变一个即可，不影响逻辑链
        # 这里需求的求解，实际过程应当是：
        # 1. 预先定义过 GetDemandOperator算子，这个算子可以接收一些输入（包括汇率），然后给出一个关于需求情况的输出
        # 2. 在这里给出对应的Term，并且执行。从而获得BeginDemand和EndDemand

        print("相对应的，故预期{}的需求将从{}提升到{}".format(GOOD, BeginDemand, EndDemand))
        print("--------------------")

        self.declare(Assertion(LHS=Term(operator=GetDemandOperator,
                                        variables=('raw petroleum', 'now')),
                               RHS=BeginDemand))
        self.declare(Assertion(LHS=Term(operator=GetDemandOperator,
                                        variables=('raw petroleum', 'future')),
                               RHS=EndDemand))

    @Rule(Exist(GOOD=MATCH.GOOD, BEGIN=MATCH.BEGIN, END=MATCH.END),
          Assertion(LHS=Term(operator=GetDemandOperator,
                             variables=('raw petroleum', 'future')),
                    RHS=8))  # 这里也没写完，不过给出了Assertion作为前提条件的例子
    # Fact(GOOD=MATCH.GOOD1, DATE=MATCH.BEGIN1, DEMAND=MATCH.DEMAND1),
    # Fact(GOOD=MATCH.GOOD2, DATE=MATCH.END1, DEMAND=MATCH.DEMAND2),
    # TEST(lambda GOOD, GOOD1, GOOD2: GOOD==GOOD1 and GOOD==GOOD2),)
    # TEST(lambda BEGIN, END, BEGIN1, END1: BEGIN==BEGIN1 and END==END1),
    # TEST(lambda DEMAND1, DEMAND2: DEMAND2 - DEMAND1 > 0))
    def D2P(self):  # , GOOD, BEGIN, END, BEGIN1, END1, DEMAND1, DEMAND2
        # print(BEGIN, END, BEGIN1, END1)
        print(1)



# engine = OurSystem()
# engine.reset()
# engine.declare(Exist(GOOD='raw petroleum', BEGIN='now', END='future'),
#                Exist(OCurrency='dollar', ICurrency='RMB', PriceType='1'),
#                Exist(IndustryClass = '申万一级行业分类'),
#                )  # Fact(operator=GetExchangerateOperator, **{'GOOD': 'raw petroleum', 'DATE': 'now', 'DEMAND': 7})
# # print(engine.facts)
# engine.run()
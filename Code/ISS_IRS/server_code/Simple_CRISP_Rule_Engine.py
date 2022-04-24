"""
Software Developer: Richard Chai
https://github.com/atsui888, atsuishisen@gmail.com
"""

import anvil.email
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

import pandas as pd
from asteval import Interpreter
aeval = Interpreter()

# Global Vars
stock_allocation = 0
bond_allocation = 0
uid = 'test_user_1234'
uid_age = 0
uid_emergency_cash_ratio = 0
uid_investment_timeframe = 0
uid_risk_tolerance = 'risk adverse'
uid_investment_objective = 'regular income'
msg_to_uid = ''


def assert_fact(ruleSet= None, entity=None, subject=None, antecedent=None, debug=False, debugL2=False):    
    """
    
    external procs should not call assert_fact() directly. they should use evaluate_fact()
    ONLY consequent functions can call assert_fact()
    
    
    1,3,5,7,9
    0+1, 1+2, 2+3, 3+4
    0+0+1, 1+1+1, 2+2+1, 3+3+1
    i+i+1 === 2*i+1
    
    entity: e.g. user_id, user_name
    ruleset: which rules to use for the evaluation (in a pandas dataframe)
    subject: which rule/s with that subject to use for evaluation
    antecedent: what is the value to compare with vs the values that exists in the ruleset.
    
    """
    ruleset_hexStr = "72756c65736574"  # hex string for 'ruleset'
    ruleset = bytearray.fromhex(ruleset_hexStr).decode()  # to avoid dataframe from auto display when imputing as fn arg
    vars = [ruleset, entity, subject,antecedent,debug,debugL2]  # standard set of vars when imputing as args into consequent function
    encode_var = lambda x: '"'+x+'"' if isinstance(x,str) else str(x)
    arg_end = ')'
    c_list = []
    
#     if debug: 
#         print("All rules in this rule set:"), display(ruleSet)    
    sc = ruleSet.subject==subject
    #oc = ruleSet.operator==operator
    #ac = ruleSet.antecedent==antecedent    
    try:
        # find the rule/s to use if it exists in the rule set
        # the rule/s should be those that match the subject 
        rules = ruleSet.loc[sc]        
        if debug: print('\nrule to be used:\n',rules)        
        
        # test the fact against the rule
        # the eval() method - substitute the value of var into the string at eval() time    
        # the aeval() method - substitue the value of var into the string before call aeval()
        # e.g. age = 17
        #      eval('age < 20')  # 17 is substitute when eval() is executed
        #      aeval('17 < 20')  # 17 must be in the string before calling aeval()

        if debug: print('\ntesting:\n\t', subject, antecedent,'\n')
        for index, row in rules.iterrows():                    
            if ('and' not in row.operator.lower()) and ('or' not in row.operator.lower()):
                if debugL2: print('this rule has no "and" and no "or".')
                # straight forward, no 'and'
                r = [str(x) for x in row[:-1]] 
                if debug: print(r)
                r[0] = str(antecedent) 
                r = ' '.join(r)
            elif ('and' in row.operator.lower()) or ('or' in row.operator.lower()) :
                if debugL2: print('this rule has "and" or "or".')                 
                t = [str(x) for x in row[:-1]]
                if debug: print(t)
                o=t[1].split()
                a=t[2].split(',')
                limit = o.count('and')
                limit+= o.count('or')
                limit +=1
                r = ''
                for i in range(limit):    
                    r += str(antecedent).strip() + str(o[i*2]).strip() + str(a[i].strip())
                    if i<limit-1:
                        r += ' ' + o[2*i+1] + ' '
            
            if debugL2: print('\ncheck if:', r)               
            
            result = aeval(r)   # result = eval(r)                                    
            if result:                
                # execute the consequent/s if the fact passes the rule testing and EXIT                                 
                if debug: print('rule passed, consequent is triggered.\n')
                c = row.consequent
                num_of_fn = c.split(',')                
                for fn in num_of_fn:                    
                    c = fn.strip()                    
                    if debugL2: print('before imputing arguments, consequent is: ',c)
                    c = c.split(')')[0]
                    for var in vars: 
                        c += encode_var(var) +','
                    c=c[:-1]        
                    c+=arg_end
                    c = c.replace('"', '', 2) 
                    next_step = eval(c) 
                    if next_step is not None:
                        c_list.append(next_step)
                    if debugL2: print('after imputing arguments, c is:',c)                                                        
                #return c_list
            else:
                # consequent not triggreed, EXIT
                if debug: print('rule not passed, no consequent.\n')
                #return c_list                        
            del r                        
    except Exception as e:
        # not found
        if debug: print('\nRule not found or',e)
            
    return c_list


          
# Consequent Functions for ISS IRS Project
"""
(Consequent Function: args)
all consequent functions have the same argument mandatory signature: `ruleset`, `entity`, `subject`,`antecedent`
they also have two optional arguments `debug`=False, `debugL2`=False. `debug` shows higher level debug statements.
`debugL2` shows more detailed statements usually variable calculations (before and after)

(Consequent Function: returns)
Two types: 
    (a) assert_fact()  -- ONLY ONE assert_fact() is allowed
    (b) return None 
It should NOT call any other type of functions unless absolutely necessary as it may create logic issues for forward chaining.

"""

def user_is_underAged(ruleset,entity,subject,antecedent, debug=False, debugL2=False):
    global msg_to_uid
    if debug:
        print('Hi {}, we look forward to serving you when you turn 18.\n'.format(entity))    
    msg_to_uid = 'Hi {}, we look forward to serving you when you turn 18. \n'.format(entity)
    return None
    
def user_is_overAged(ruleset,entity,subject,antecedent, debug=False, debugL2=False):
    global msg_to_uid
    if debug:
        print('Hi {}, investing comes with inherent volatility, please consider carefully.\n'.format(entity))
    msg_to_uid = 'Hi {}, investing comes with inherent volatility, please consider carefully.\n'.format(entity)
    return None

def user_is_potential_client(ruleset,entity,subject,antecedent, debug=False, debugL2=False):
    global stock_allocation, bond_allocation, msg_to_uid
    stock_allocation = 100-antecedent
    bond_allocation = antecedent
    if debug:
        print('Your portfolio is initially allocated as: stock: {}%, bond: {}%\n'.format(stock_allocation, bond_allocation))
    msg_to_uid = 'Your portfolio is initially allocated as: stock: {}%, bond: {}%\n'.format(stock_allocation, bond_allocation)
    return "assert_fact(ruleset,entity,subject='emergency cash',antecedent=uid_emergency_cash_ratio,debug=debug, debugL2=debugL2)"    
    

def user_is_potentially_insolvent(ruleset,entity,subject,antecedent, debug=False, debugL2=False):  
    global stock_allocation, bond_allocation, msg_to_uid
    stock_allocation = 0
    bond_allocation = 0
    if debug:
        print('Hi {}, we suggest you grow your emergency cash funds as a priority.\n'.format(entity))
        print('Your portfolio is initially allocated as: stock: {}%, bond: {}%\n'.format(stock_allocation, bond_allocation))
    txt1 = 'Hi {}, we suggest you grow your emergency cash funds as a priority.\n'.format(entity)
    txt2 = 'Your portfolio is initially allocated as: stock: {}%, bond: {}%\n'.format(stock_allocation, bond_allocation)
    msg_to_uid = txt1+txt2    
    return None   

def user_is_solvent(ruleset,entity,subject,antecedent, debug=False, debugL2=False):
    return "assert_fact(ruleset,entity,subject='investment timeframe',antecedent=uid_investment_timeframe,debug=debug, debugL2=debugL2)"    

def user_investTF_less6Mths(ruleset,entity,subject,antecedent, debug=False, debugL2=False):
    global stock_allocation, bond_allocation, msg_to_uid    
    if debug: print('portfolio is, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))    
    stock_allocation = 0
    bond_allocation = 100
    if debug:        
        print('stock is set to 0%, bond is set to 100%')
        print('portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))    
    txt1 = 'stock is set to 0%, bond is set to 100%'
    txt2 = ' portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation)
    msg_to_uid = txt1+txt2    
    return None


def user_investTF_greaterEq6Mths(ruleset,entity,subject,antecedent, debug=False, debugL2=False):
    if debug: print('user investment timeframe >= 6 months')
    if uid_risk_tolerance == 'very risk adverse':
        return "assert_fact(ruleset,entity,subject='very risk adverse',antecedent=True,debug=debug, debugL2=debugL2)"
    elif uid_risk_tolerance == 'risk adverse':
        return "assert_fact(ruleset,entity,subject='risk adverse',antecedent=True,debug=debug, debugL2=debugL2)"
    elif uid_risk_tolerance == 'risk tolerant':
        return "assert_fact(ruleset,entity,subject='risk tolerant',antecedent=True,debug=debug, debugL2=debugL2)"
    elif uid_risk_tolerance == 'very risk tolerant':
        return "assert_fact(ruleset,entity,subject='very risk tolerant',antecedent=True,debug=debug, debugL2=debugL2)"
    

def user_is_very_risk_adverse(ruleset,entity,subject,antecedent, debug=False, debugL2=False):    
    global stock_allocation, bond_allocation, msg_to_uid
    if debug: print('portfolio is, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))    
    stock_allocation = 0
    bond_allocation = 100
    if debug: 
        print('very risk adverse')        
        print('stock is set to 0%, bond is set to 100%')
        print('portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))
    txt1 = 'stock is set to 0%, bond is set to 100%'
    txt2 = ' portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation)
    msg_to_uid = txt1 + txt2
    return None  

def user_is_risk_adverse(ruleset,entity,subject,antecedent, debug=False, debugL2=False):    
    global stock_allocation, bond_allocation, msg_to_uid
    if debug: print('portfolio is, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))    
    stock_allocation +=5
    bond_allocation -=5
    if debug: 
        print('risk adverse')        
        print('stock is set to +5%, bond is set to -5%')
        print('portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))
    
    txt1 = 'stock is set to +5%, bond is set to -5%'
    txt2 = ' portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation)
    msg_to_uid = txt1 + txt2
    
    if uid_investment_objective == 'capital growth':
        return "assert_fact(ruleset,entity,subject='capital growth',antecedent=True,debug=debug, debugL2=debugL2)"
    elif uid_investment_objective == 'balanced growth and income':
        return "assert_fact(ruleset,entity,subject='balanced growth and income',antecedent=True,debug=debug, debugL2=debugL2)"
    elif uid_investment_objective == 'regular income':
        return "assert_fact(ruleset,entity,subject='regular income',antecedent=True,debug=debug, debugL2=debugL2)"
    
    
def user_is_risk_tolerant(ruleset,entity,subject,antecedent, debug=False, debugL2=False):
    global stock_allocation, bond_allocation, msg_to_uid
    if debug: print('portfolio is, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))    
    stock_allocation +=10
    bond_allocation -=10
    if debug: 
        print('risk tolerant')        
        print('stock is set to +10%, bond is set to -10%')
        print('portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))        
    txt1 = 'stock is set to +10%, bond is set to -10%'
    txt2 = ' portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation)
    msg_to_uid=txt1+txt2
        
    if uid_investment_objective == 'capital growth':
        return "assert_fact(ruleset,entity,subject='capital growth',antecedent=True,debug=debug, debugL2=debugL2)"
    elif uid_investment_objective == 'balanced growth and income':
        return "assert_fact(ruleset,entity,subject='balanced growth and income',antecedent=True,debug=debug, debugL2=debugL2)"
    elif uid_investment_objective == 'regular income':
        return "assert_fact(ruleset,entity,subject='regular income',antecedent=True,debug=debug, debugL2=debugL2)"
        
    
def user_is_very_risk_tolerant(ruleset,entity,subject,antecedent, debug=False, debugL2=False):
    global stock_allocation, bond_allocation, msg_to_uid
    if debug: print('portfolio is, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))    
    stock_allocation +=15
    bond_allocation -=15
    if debug: 
        print('very risk tolerant')        
        print('stock is set to +15%, bond is set to -15%')
        print('portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))
    txt1 = 'stock is set to +15%, bond is set to -15%'
    txt2 = ' portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation)
    msg_to_uid = txt1 + txt2
        
    if uid_investment_objective == 'capital growth':
        return "assert_fact(ruleset,entity,subject='capital growth',antecedent=True,debug=debug, debugL2=debugL2)"
    elif uid_investment_objective == 'balanced growth and income':
        return "assert_fact(ruleset,entity,subject='balanced growth and income',antecedent=True,debug=debug, debugL2=debugL2)"
    elif uid_investment_objective == 'regular income':
        return "assert_fact(ruleset,entity,subject='regular income',antecedent=True,debug=debug, debugL2=debugL2)"

    
def user_wants_capitalGrowth(ruleset,entity,subject,antecedent, debug=False, debugL2=False):
    global stock_allocation, bond_allocation, msg_to_uid
    if debug: print('portfolio is, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))    
    stock_allocation +=15
    bond_allocation  -=15
    if debug: 
        print('capital growth')        
        print('stock is set to +15%, bond is set to -15%')
        print('portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))
    
    txt1 = 'stock is set to +15%, bond is set to -15%'
    txt2 = 'portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation)
    msg_to_uid = txt1 + txt2
    return None
    
def user_wants_balancedGrowthIncome(ruleset,entity,subject,antecedent, debug=False, debugL2=False):
    if debug: print('portfolio is, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))
    if debug: 
        print('balanced growth and income')        
        print('no change to stock or bond allocations')
        print('portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))
    return None

def user_wants_regularIncome(ruleset,entity,subject,antecedent, debug=False, debugL2=False):
    global stock_allocation, bond_allocation, msg_to_uid
    if debug: print('portfolio is, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))    
    stock_allocation -=15
    bond_allocation  +=15
    if debug: 
        print('regular income')        
        print('stock is set to -15%, bond is set to +15%')
        print('portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation))
    txt1 = 'stock is set to -15%, bond is set to +15%'
    txt2 = ' portfolio is now, stock: {}, bond: {}'.format(stock_allocation, bond_allocation)
    msg_to_uid=txt1 + txt2
    return None
    

# Rules for ISS IRS project
"""
    Rules must have `subject`, `operator`,`antecedent` and `consequent` for it to function properly
    There can be more than one consequent functions for each rule. 
    

"""

data = {
    'subject': ['age','age','age','emergency cash','emergency cash','investment timeframe','investment timeframe',
               'very risk adverse','risk adverse','risk tolerant','very risk tolerant',
                'capital growth','balanced growth and income','regular income'],
    'operator':['<','>','>= and <=','<','>=','<','>=','==','==','==','==','==','==','=='],
    'antecedent':[18,100,"18, 100",6,6,6,6,True,True,True,True,True,True,True],
    'consequent':['user_is_underAged()','user_is_overAged()','user_is_potential_client()',
                  'user_is_potentially_insolvent()','user_is_solvent()',
                 'user_investTF_less6Mths()','user_investTF_greaterEq6Mths()',
                 'user_is_very_risk_adverse()','user_is_risk_adverse()','user_is_risk_tolerant()','user_is_very_risk_tolerant()',
                 'user_wants_capitalGrowth()','user_wants_balancedGrowthIncome()','user_wants_regularIncome()']
}

df = pd.DataFrame(data)

@anvil.server.callable
def call_simple_crisp_engine(t_id, id_age,id_emergency_cash_ratio,id_investment_timeframe
                             ,id_risk_tolerance,id_investment_objective):
  global stock_allocation, bond_allocation
  global uid,uid_age,uid_emergency_cash_ratio,uid_investment_timeframe,uid_risk_tolerance,uid_investment_objective
  
  uid = t_id  # hard-coded for POC
  uid_age = id_age
  uid_emergency_cash_ratio = id_emergency_cash_ratio
  uid_investment_timeframe = id_investment_timeframe
  uid_risk_tolerance = id_risk_tolerance
  uid_investment_objective = id_investment_objective
  
  ruleset = df
  entity  = uid
  subject = 'age'
  antecedent = uid_age
  
  evaluate_fact(ruleset,entity,subject,antecedent, debug=False, debugL2=False)
  if stock_allocation>100: stock_allocation=100
  if stock_allocation<0: stock_allocation=0
  if bond_allocation>100: bond_allocation=100
  if bond_allocation<0: bond_allocation=0
  
  return (stock_allocation, bond_allocation, msg_to_uid)

def evaluate_fact(ruleset,entity,subject,antecedent, debug=False, debugL2=False):
    cont = True
    results = assert_fact(ruleset,entity,subject,antecedent, debug=debug, debugL2=debugL2)    
    while cont:
        #if results is not None:            
        if len(results)>0:
            if debug: print(results)    
            for r in results:
                results=eval(r)
        else: cont = False
    



          
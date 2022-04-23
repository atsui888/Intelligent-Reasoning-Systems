"""
Software Developer: Richard Chai
https://github.com/atsui888, atsuishisen@gmail.com
"""

from ._anvil_designer import Investor_ProfileTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Investor_Profile(Investor_ProfileTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.uid = 'uid_101'  # hardcoded for this deo
    self.uid_age = 0    
    self.uid_emergency_cash_ratio = 0  # in months
    self.uid_investment_timeframe = 0 # in months
    # 'very risk adverse' | 'risk adverse' | 'risk tolerant' | 'very risk tolerant'
    self.uid_risk_tolerance = 'risk adverse'
    # 'capital growth', 'balanced growth and income', 'regular income'
    self.uid_investment_objective = 'regular income'
    self.dd_riskTolerance.selected_value_int = 0
    self.dd_investObjectives.selected_value_int = 0
    
    
    
  def btn_recommend_investment_portfolio_click(self, **event_args):
    """This method is called when the button is clicked"""
    error = False
    errorTxt = "Please let us know the following:"   
    # age
    if self.dd_age.selected_value == "Select":      
      errorTxt += "\n- your age"    
      error = True
    elif self.dd_age.selected_value == '<18':
      self.uid_age = 17
    elif self.dd_age.selected_value == '>100':
      self.uid_age = 101
    else:
      self.uid_age = int(self.dd_age.selected_value)     
      
    # emergency cash ratio
    if len(self.tb_emergency_cash.text)<1:
      errorTxt += "\n- emergency cash fund"
      error = True
    if len(self.tb_monthlyExpense.text)<1:
      errorTxt += "\n- monthly expense"
      error = True    
    if len(self.lbl_emergencyCashRatio.text)>0:
      self.uid_emergency_cash_ratio = float(self.lbl_emergencyCashRatio.text)
    # investment timeframe    
    if self.dd_investTimeFrame.selected_value=="Select":
      errorTxt += "\n- your investment timeframe"    
      error = True            
    elif self.dd_investTimeFrame.selected_value == '< 6 months':
        self.uid_investment_timeframe = 5        
    elif self.dd_investTimeFrame.selected_value == '>= 6 months':
        self.uid_investment_timeframe = 7      
    
    # risk tolerance
    if self.dd_riskTolerance.selected_value=="Select":
      errorTxt += "\n- your risk tolerance preference"    
      error = True  
    elif self.dd_riskTolerance.selected_value=="Don't want to lose any money at all":
      self.uid_risk_tolerance = 'very risk adverse'
      self.dd_riskTolerance.selected_value_int = 1
    elif self.dd_riskTolerance.selected_value=="A little risk to keep pace with inflation":
      self.uid_risk_tolerance = 'risk adverse'
      self.dd_riskTolerance.selected_value_int = 2
    elif self.dd_riskTolerance.selected_value=="Some risk and fluctuations for higher potential returns":
      self.uid_risk_tolerance = 'risk tolerant'
      self.dd_riskTolerance.selected_value_int = 3
    elif self.dd_riskTolerance.selected_value=="Significant Risk to maximize returns":
      self.uid_risk_tolerance = 'very risk tolerant'
      self.dd_riskTolerance.selected_value_int =4
      
    # investment objectives
    if self.dd_investObjectives.selected_value=="Select":
      errorTxt += "\n- your investment objectives"
      error = True  
    elif self.dd_investObjectives.selected_value=="Focus on capital growth":
      self.uid_investment_objective='capital growth'
      self.dd_investObjectives.selected_value_int = 1
    elif self.dd_investObjectives.selected_value=="Balance capital growth and income generation":
      self.uid_investment_objective='balanced growth and income'
      self.dd_investObjectives.selected_value_int = 2
    elif self.dd_investObjectives.selected_value=="Regular income":
      self.uid_investment_objective='regular income'
      self.dd_investObjectives.selected_value_int = 3

    #self.temp_display.text=self.uid_investment_objective
      
    if error:
      errorTxt += "\nso that we can better assist you."
      alert(errorTxt)
      #alert('Form is not submitted)')
    else:
        # no errors, submit the form
        #Notification("Form submitted!").show()
        # run eval_fact() code
        
        t_id = 'uid_101'  # hardcode for this POC
        stock_allocation, bond_allocation, msg_to_uid = \
        anvil.server.call('call_simple_crisp_engine',t_id,self.uid_age,
                          self.uid_emergency_cash_ratio,
                          self.uid_investment_timeframe,
                          self.uid_risk_tolerance,
                          self.uid_investment_objective )
        self.lbl_stock_pct.text=stock_allocation
        self.lbl_bond_pct.text=bond_allocation
        self.temp_display.text = msg_to_uid
        
        # Send User Details to Collaborative Filtering Server and get recommendation
#         risk_appetite = {
#           'do not wish to lose any money at all':1,
#           'a little risk to keep pace with inflation':2,
#           'some risk and fluctuations for higher potential returns':3,
#           'significant risk to maximise returns':4
#         }
#         investment_objective = {
#           'focus on capital growth':1,
#           'balance capital growth and income generation':2,
#           'regular income':3
#         }
        
        data = {
          'user_id': [self.uid],          
          'risk_appetite': [self.dd_riskTolerance.selected_value_int],
          'investment_objective': [self.dd_investObjectives.selected_value_int],
          'equities_alloc':  [stock_allocation], 
          'bonds_alloc': [bond_allocation]    
        }
        
        #open_form('Potential_Returns',stock_allocation, bond_allocation)
        open_form('Potential_Returns',stock_alloc=stock_allocation, 
                  bond_alloc=bond_allocation, user_data=data)

    # alert("Submitting the Form now.")
    
  def clear_inputs(self):
  # Clear our three text boxes
    self.dd_age.selected_value="Select"
    self.tb_emergency_cash.text=''
    self.tb_monthlyExpense.text=''
    self.lbl_emergencyCashRatio.text=''
    self.dd_investTimeFrame.selected_value="Select"
    self.dd_riskTolerance.selected_value="Select"
    self.dd_investObjectives.selected_value="Select"
    #alert('clearing form')

  def tb_monthlyExpense_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    pass

  def tb_monthlyExpense_lost_focus(self, **event_args):
    """This method is called when the TextBox loses focus"""    
    self.emergencyCashRatio=float(self.tb_emergency_cash.text)/float(self.tb_monthlyExpense.text)
    self.lbl_emergencyCashRatio.text=str(self.emergencyCashRatio)
    pass

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.clear_inputs()


  

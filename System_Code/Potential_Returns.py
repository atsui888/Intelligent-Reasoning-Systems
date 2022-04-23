"""
Software Developer: Richard Chai
https://github.com/atsui888, atsuishisen@gmail.com
"""

from ._anvil_designer import Potential_ReturnsTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Potential_Returns(Potential_ReturnsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)   

    # Any code you write here will run when the form opens.
    self.selected_stock_ticker=''
    self.stock_allocation = properties['stock_alloc']
    self.bond_allocation = properties['bond_alloc']
    self.lbl_portfolio_allocation.text = f'Stock: {self.stock_allocation}%, \
    Bond: {self.bond_allocation}%'
    
    #print(properties['user_data'])
    #print()
    if self.bond_allocation>0:
      result = anvil.server.call('add_new_user_to_user_profiles', properties['user_data'])
      # currently, top_k set to 1, so only one result, hence[0]
      # result[0]['fund_chosen'] + str(result[0]['recommendation_score']/5) + str(result[0]['investment_returns'])    
      tmp_str = '"{}", \tScore: {:.2f}, \tExpected Returns: {:.2f}%'.format(
      result[0]['fund_chosen'],result[0]['recommendation_score']/5,
      result[0]['investment_returns']
      )
      self.lbl_bond_funds.text = tmp_str
      self.projected_bond_returns = result[0]['investment_returns']
      
      tmp_str = '"{}", Score: {:.2f}, \tExpected Returns: {:.2f}%'.format(
      result[1]['fund_chosen'],result[1]['recommendation_score']/5,
      result[1]['investment_returns']
      )
      
      tmp_str2 = '"{}", Score: {:.2f}, \tExpected Returns: {:.2f}%'.format(
      result[2]['fund_chosen'],result[2]['recommendation_score']/5,
      result[2]['investment_returns']
      )
      
      tmp_str3 = 'Not Selected:\n'+tmp_str + '\n' + tmp_str2
      self.lbl_bond_funds_discarded.text = tmp_str3
    else:
      self.lbl_bond_funds.text = 'None - 0%'
      self.projected_bond_returns = 0      
    
    self.portfolio_holding_period_yrs = 5.0
    #self.projected_stock_returns = round(5,2)
    #self.lbl_stk_returns.text=str(round(self.projected_stock_returns,2))+'%'
    
    #self.projected_portfolio_position = round(self.calc_portfolio_position(),2)
    #self.lbl_portfolio_position.text= str(self.projected_portfolio_position)+'%'
    
    # get stock forecast
    forecast = anvil.server.call('arima_main', 'AAPL')
    
    #print(forecast[-1])
    px_begin = forecast[int(3/8 * len(forecast))]['predicted_mean'] 
    px_end = forecast[-1]['predicted_mean']
    self.projected_stock_returns = round((px_end-px_begin)/px_begin*100,2)
    #self.lbl_stk_returns.text=str(round(self.projected_stock_returns,2))+'%'
    tempRet = str(round(self.projected_stock_returns,2))
    tempRet = tempRet.split('.')[0] + '%'
    self.lbl_stk_returns.text=tempRet
    #self.lbl_stk_returns.text = '999'
    
    
    self.projected_portfolio_position = round(self.calc_portfolio_position(),0)+1
    self.lbl_portfolio_position.text= str(self.projected_portfolio_position).split('.')[0] +'%'

        
    
  def calc_portfolio_position(self):
    portfolio_returns = round(((
      ( 
        #(self.stock_allocation/100  * (1+self.projected_stock_returns/100)**self.portfolio_holding_period_yrs)
        (self.stock_allocation * self.projected_stock_returns/100)  # stock returns ALREADY calc for 5 years
        + (self.bond_allocation/100 * (1+self.projected_bond_returns/100)**self.portfolio_holding_period_yrs)
      ) ) - 1)  ,2)    
    return portfolio_returns

  def back_to_investor_profile_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Investor_Profile')
    pass

  def btn_get_stk_forecast_click(self, **event_args):
    self.selected_stock_ticker = self.dd_stock_ticker.selected_value
    #print(self.selected_stock_ticker)
    forecast = anvil.server.call('arima_main', self.selected_stock_ticker)
    
    #print(forecast[-1])
    px_begin = forecast[int(3/8 * len(forecast))]['predicted_mean'] 
    px_end = forecast[-1]['predicted_mean']
    self.projected_stock_returns = round((px_end-px_begin)/px_begin*100,2)
    #self.lbl_stk_returns.text=str(round(self.projected_stock_returns,2))+'%'
    tempRet = str(round(self.projected_stock_returns,2))
    tempRet = tempRet.split('.')[0] + '%'
    self.lbl_stk_returns.text=tempRet
    #self.lbl_stk_returns.text = '999'
    
    
    self.projected_portfolio_position = round(self.calc_portfolio_position(),0)+1
    self.lbl_portfolio_position.text= str(self.projected_portfolio_position)+'%'
        
    from plotly import graph_objects as go

    self.rich_text_2.visible=True
    
    # Plot some data
    X_values = [item['index'].strftime('%Y-%m-%d') for item in forecast]
    y_values = [round(item['predicted_mean'],2) for item in forecast]
    self.plot_1.data = [
      go.Scatter(
        x = X_values,
        y = y_values,
        marker = dict(
          color= 'rgb(16, 32, 77)'
        )
      ),
    ]
    

  
#   def view_stock_chart(self):
#         # Plot some data
#     self.plot_1.data = [
#       go.Scatter(
#         x = [1, 2, 3],
#         y = [3, 1, 6],
#         marker = dict(
#           color= 'rgb(16, 32, 77)'
#         )
#       ),
#       go.Bar(
#         x = [1, 2, 3],
#         y = [3, 1, 6],
#         name = 'view stock data Example'
#       )
#     ]

    pass


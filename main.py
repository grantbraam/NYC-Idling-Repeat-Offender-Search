from flask import Flask, request, redirect, render_template
from nyc_idling_prior_offense_search import prior_violation_find

app = Flask(
  __name__,
  template_folder='templates',
  static_folder='static'
)

@app.route('/')
def input():
    return render_template('input.html')

container = {}

@app.route('/', methods=['POST'])
def my_form_post():
  container['state'] = request.form['state']
  container['plate'] = request.form['plate']
  container['viol_date'] = request.form['viol_date']
  return redirect('/output', code=302)

  
@app.route('/output')
def prior_viol_search():
    #The HTML template ignores native Unix/Python linebreaks and won't render HTML. Spit on
    #the HTML tags and reapply them for the template to render.
    text_output = prior_violation_find(container['state'],container['plate'] ,container['viol_date'])
    text_array = text_output.split('<br>')
    return render_template('output.html', idling_viol_text=text_array)
     

if __name__ == "__main__":
  app.run(
    host='0.0.0.0',
    debug = True,
    port=8080
  )

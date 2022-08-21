from flask import Flask, request,jsonify,session
from Pair import getpairs, profits

app = Flask(__name__)
app.url_map.strict_slashes = False


@app.route('/getpair',methods = ['POST','GET'])
def pair():
  if request.method =="POST":
    sy = str(request.json['startyear'])
    sm = str(request.json['startmonth'])
    sd = str(request.json['startday'])
    ey = str(request.json['endyear'])
    em = str(request.json['endmonth'])
    ed = str(request.json['endday'])
    startdate = sy+'-'+sm+'-'+sd
    enddate = ey+'-'+em+'-'+ed

    pairs= getpairs(startdate,enddate)

    results = {"s11":pairs[0][0],
               "s12": pairs[0][1],
               "s21": pairs[1][0],
               "s22": pairs[1][1],
               "s31": pairs[2][0],
               "s32": pairs[2][1],}
    return jsonify(results)


@app.route('/btpair',methods = ['POST','GET'])
def bt():
  if request.method == "POST":
    s1 = str(request.json['stock1'])
    s2 = str(request.json['stock2'])
    sy = str(request.json['startyear'])
    sm = str(request.json['startmonth'])
    sd = str(request.json['startday'])
    ey = str(request.json['endyear'])
    em = str(request.json['endmonth'])
    ed = str(request.json['endday'])
    enter_z = str(request.json['enter_z'])
    exit_z = str(request.json['exit_z'])
    r_level = str(request.json['risk_level'])
    risk = [enter_z,exit_z,r_level]
    startdate = sy + '-' + sm + '-' + sd
    enddate = ey + '-' + em + '-' + ed
    pair = [s1,s2]
    log = profits(pair,startdate,enddate,risk)
    results = {}

    i=1
    for entry in log:

      results[i] = entry
      i=i+1
    return jsonify(results)


if __name__ == "__main__":
  app.run()

from flask import Flask, render_template, request
import mysql.connector

mydb = mysql.connector.connect(host="127.0.0.1",
                                user="root",
                                password="21072000",
                                database="ars2",
                                auth_plugin='mysql_native_password')
mycursor = mydb.cursor()
# mycursor.execute("select username from users")
# for i in mycursor.fetchone():
#     print(i)

app = Flask(__name__)

curr_user = ""
a_code = ""

@app.route('/')
def signUp():
    return render_template("signUp.html")

@app.route('/signIn', methods = ['POST', 'GET'])
def signIn():
    if request.method == 'POST':
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        confirmPassword = request.form["confirmPassword"]
        dob = request.form["dob"]
        phno1 = int(request.form["phno1"])
        phno2 = int(request.form["phno2"])

        myquery = "select exists(select * from users where username=%s)"
        rec_tup = (username,)
        mycursor.execute(myquery, rec_tup)
        if mycursor.fetchone()[0]==1:
            return '<body>Username already exists</body>'
        elif password!=confirmPassword:
            return '<body>Passwords dont match</body>'
        else:
            mysql_query = "insert into users values(%s, %s, %s, %s)"
            records = (username, name, password, dob)
            mycursor.execute(mysql_query, records)
            print(name, username, password, dob)
            mydb.commit()

            mysql_query = "insert into user_contacts values(%s, %s)"
            records = (username, phno1)
            mycursor.execute(mysql_query, records)
            mydb.commit()

            mysql_query = "insert into user_contacts values(%s, %s)"
            records = (username, phno2)
            mycursor.execute(mysql_query, records)
            mydb.commit()

            return render_template("signIn.html")

@app.route('/alreadyMember', methods = ['POST', 'GET'])
def alreadyMemeber():
    if request.method == 'POST':
        return render_template("signIn.html")

@app.route('/goAdminSignIn', methods = ['POST', 'GET'])
def goAdminSignIn():
    if request.method == 'POST':
        return render_template("adminSignIn.html")

@app.route('/adminHome', methods = ['POST', 'GET'])
def adminHome():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username=="sarvagna" and password=="sarvagna":
            return render_template("adminHomePage.html")
        else:
            return '<body>Wrong Admin Username/Password</body>'

@app.route('/updatedSeats', methods = ['POST', 'GET'])
def updatedSeats():
    if request.method == "POST":
        acode = request.form["acode"]
        seats = request.form["seats"]

        myquery = "select exists(select * from airplane where a_code=%s)"
        record = (acode, )
        mycursor.execute(myquery, record)
        if mycursor.fetchone()[0]==1:
            myquery = "update airplane set tot_seats=%s where a_code=%s"
            record = (seats, acode)
            mycursor.execute(myquery, record)
            mydb.commit()
            return render_template("signUp.html")
        else:
            return '<body>No Such Airplane Code Found</body>'



@app.route('/home', methods = ['POST', 'GET'])
def home():
    global curr_user
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        myquery = "select exists(select * from users where username=%s)"
        rec_tup = (username,)
        mycursor.execute(myquery, rec_tup)
        if mycursor.fetchone()[0]==1:
            new_query = "select password from users where username=%s"
            mycursor.execute(new_query, rec_tup)
            if mycursor.fetchone()[0]==password:
                curr_user = username
                return render_template("homePage.html")
            else:
                return '<body>Username/Password Wrong</body>'
        else:
            return '<body>Username/Password Wrong</body>'

@app.route('/flights', methods = ['POST', 'GET'])
def flights():
    global a_code
    if request.method == 'POST':
        fromDest = request.form["from"]
        toDest = request.form["to"]
        #depDate = request.form["depDate"]
        classF = request.form["classF"]

        myquery = "select exists(select fd.flight_id, fd.a_code,fd.arrTime, fd.depTime, r.from_dest, r.to_dest, f.class, f.fare from flightdet fd join route r on fd.route_id = r.route_id join fare f on r.route_id=f.route_id where class=%s and r.from_dest=%s and r.to_dest=%s) as y"
        rec_tup = (classF, fromDest, toDest)
        #print(classF, fromDest, toDest)
        mycursor.execute(myquery, rec_tup)
        if mycursor.fetchone()[0]==1:
            myquery = "select fd.flight_id, fd.a_code,fd.arrTime, fd.depTime, r.from_dest, r.to_dest, f.class, f.fare from flightdet fd join route r on fd.route_id = r.route_id join fare f on r.route_id=f.route_id where class=%s and r.from_dest=%s and r.to_dest=%s"
            mycursor.execute(myquery, rec_tup)
            data = mycursor.fetchall()
            #for i in data:
            #    print(i)
            return render_template("flights.html", data = data)
        else:
            return "<body>No Flights Found according to your choices</body>"

@app.route('/booked', methods = ['POST', 'GET'])
def booked():
    global a_code
    if request.method == 'POST':
        flight_id = request.form["flight_id"]
        acode = request.form["acode"]
        classF = request.form["class"]
        fare = request.form["fare"]   

        # myquery = "insert into carries(a_code, username) values(%s, %s)"
        # rec_tup = (acode, curr_user)
        # print(acode, curr_user)
        # mydb.commit()
        
        myquery = "insert into bookings(username, flight_id, class, fare) values(%s, %s, %s, %s)"
        rec_tup = (curr_user, flight_id, classF, fare)
        mycursor.execute(myquery, rec_tup)
        mydb.commit()

        return render_template("homePage.html")

@app.route('/signout', methods = ['POST', 'GET'])
def signout():
    if request.method == 'POST':
        return render_template("signUp.html")


@app.route('/myflights', methods = ['POST', 'GET'])
def myflights():
    if request.method == "POST":

        myquery = "select b.booking_id, b.flight_id, r.from_dest, r.to_dest, fd.arrTime, fd.depTime, b.class from bookings b join flightdet fd on b.flight_id = fd.flight_id join route r on fd.route_id = r.route_id where username=%s"
        rec_tup = (curr_user, )
        mycursor.execute(myquery, rec_tup)
        data = mycursor.fetchall()

        return render_template("myFlights.html", data = data)

@app.route('/searchFlight', methods = ['POST', 'GET'])
def searchFlight():
    if request.method == "POST":
        booking_id = request.form["booking_id"]

        myquery = "select u.fullname, b.flight_id, b.fare from users u join bookings b on u.username = b.username where booking_id=%s"
        rec_tup = (booking_id, )
        mycursor.execute(myquery, rec_tup)
        data = mycursor.fetchall()

        return render_template("searchFlights.html", data = data)



if __name__ == "__main__":
    
    app.run(debug=True, port=8080)
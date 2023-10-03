import mysql.connector
import os
import datetime
import glob

from pathlib import Path

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def check_documentdirs(documentdirs, rootpath):

    listindex = 0

    # Val is list of tuples
    #
    # 0 == Personid
    # 1 == Lastname
    # 2 == Firstname
    # 3 == Document Path
    #
    # Logentrytypeid
    #
    # 1 == Error
    # 2 == Warning
    # 3 == Information
    #
    # Logactivityid
    #
    # 1 == Scan document paths

    for val in documentdirs:

        pathtocheck = rootpath + val[3]

        if os.path.isdir(pathtocheck):
            print(str(val[0]) + ", " + val[3] + " does exist")
        else:
            print(str(val[0]) + ", " + val[3] + " doesn't exist")
            logtext = "Warning:  Document path '{0}' specified for person '{1}, {2}' does not exist.  Fix database settings for this person.".format(val[3], val[1], val[2])
            write_logentry(logtext, "system", 1, 1)

            # Remove entry from list of tuples
            del documentdirs[listindex]

        listindex += 1

def write_logentry(logentrytext, logentryuser, logentrytypeid, logactivitytypeid):

    current_datetime = datetime.datetime.now()

    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="biologydb"
    )

    mycursor = mydb.cursor()

    sql = "INSERT INTO data_log (loggeddate, logentrytypeid, logactivitytypeid, logtext, userid) VALUES (%s, %s, %s, %s, %s)"
    val = (current_datetime, logentrytypeid, logactivitytypeid, logentrytext, logentryuser)
    mycursor.execute(sql, val)

    mydb.commit()

def get_people_with_document_directories():

    # Get all persons with document directories

    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="biologydb"
    )
    mycursor = mydb.cursor()

    mycursor.execute("select id, lastname, firstname, documentfilepath from data_persons where documentfilepath != ''")

    myresult = mycursor.fetchall()

    return myresult

# def personfilerecordexists(filename, personid):
#     mydb = mysql.connector.connect(
#       host="localhost",
#       user="root",
#       password="",
#       database="biologydb"
#     )
#     mycursor = mydb.cursor()
#
#     sqlstatement = "SELECT id FROM data_person_documents where personid = " + str(personid) + " and filename = '" + filename + "'"
#     mycursor.execute(sqlstatement)
#
#     myresult = mycursor.fetchall()
#
#     if len(myresult) == 0:
#         return False
#     else:
#         return True

# def updatedatabase(personid, personfilenames):

    # for personfilename in personfilenames:
    #     if not personfilerecordexists(personfilename, personid):
    #         addpersonfilerecord(print("Hello Dave")

def get_person_documents_from_db(personid):
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="biologydb"
    )
    mycursor = mydb.cursor()

    sqlstatement = "SELECT id, filename FROM data_person_documents where personid = " + str(personid)
    mycursor.execute(sqlstatement)

    return mycursor.fetchall()

def get_person_documents_from_directory(personid):

    # Get person's document directory
    print("Hi Dave")

def comparefilelists(personfilesfromdb, personfilesfromdirectory):

    returnlist = []

    matchfound = False

    # Loop through all files found in the directory
    for personfilefromdirectory in personfilesfromdirectory:

        # Look for any added files
        matchfound = False
        for personfilefromdb in personfilesfromdb:
            if personfilefromdb[1] == personfilefromdirectory:
                matchfound = True
                break

        if not matchfound:
            returnlist.append(["Add", personfilefromdirectory])

    if len(personfilesfromdb) > 1:
        print("Hi Dave")

    # Loop through all files in the database
    for personfilefromdb in personfilesfromdb:

        # Look for any added files
        matchfound = False
        for personfilefromdirectory in personfilesfromdirectory:
            if personfilefromdb[1] == personfilefromdirectory:
                matchfound = True
                break

        if not matchfound:
            returnlist.append(["Remove", personfilefromdb[1]])

    return returnlist

def updatedatabase(personid, personlastname, personfirstname, databaseupdates):

    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="biologydb"
    )
    mycursor = mydb.cursor()
    for databaseupdate in databaseupdates:

        # Handle "adds"
        if databaseupdate[0] == "Add":

            # Code Document Type
            #
            # 5 == Unknown document type

            # Perform the update to database
            sqlstatement = "insert into data_person_documents (personid, documenttypeid, filename) VALUES (%s, %s, %s)"
            val = (str(personid), "5", databaseupdate[1])
            mycursor.execute(sqlstatement, val)
            mydb.commit()

            # Log the update <= Working here

            # Logentrytypeid
            #
            # 1 == Error
            # 2 == Warning
            # 3 == Information
            #
            # Logactivityid
            #
            # 1 == Scan document paths

            logtext = "Added document '{0}' for person '{1}, {2}'".format(databaseupdate[1], personlastname, personfirstname)
            sqlstatement = "insert into data_log (loggeddate, logentrytypeid, logactivitytypeid, logtext, userid) VALUES (now(), %s, %s, %s, 'system')"
            val = (3, 1, logtext)
            mycursor.execute(sqlstatement, val)
            mydb.commit()

        elif databaseupdate[0] == "Remove":

            # Perform the update to database
            sqlstatement = 'delete from data_person_documents where personid = {0} and filename = "{1}"'.format(str(personid), databaseupdate[1])
            mycursor.execute(sqlstatement)
            mydb.commit()

            # Log the update
            logtext = "Deleted document '{0}' for person '{1}, {2}'".format(databaseupdate[1], personlastname, personfirstname)
            sqlstatement = "insert into data_log (loggeddate, logentrytypeid, logactivitytypeid, logtext, userid) VALUES (now(), %s, %s, %s, 'system')"
            val = (3, 1, logtext)
            mycursor.execute(sqlstatement, val)
            mydb.commit()


def gettreewalkedfilenames(documentdir, rootpath):

    startingpath = rootpath + documentdir
    filenames = []

    # for root, dirs, files in os.walk(startingpath):
    #     for filename in files:
    #         # doSomethingWithFile(os.path.join(root, filename))
    #     # for dirname in dirs:
    #     #     doSomewthingWithDir(os.path.join(root, dirname))
    #         filenames.append(os.path.join(root,filename))

    # for p in Path(startingpath).rglob(startingpath + "*"):
    #     # for p in Path(startingpath).rglob('*'):
    #     print(p)
    #     filenames.append(p)

    actualdirectorycontents = sorted(Path(startingpath).rglob('*'))
    databasedirectorycontents = get_person_documents_from_db(personid)

    for item in actualdirectorycontents:
        if item.is_file():
            itemparent = str(Path(item.parent))

            # Hack
            itemparent = itemparent.replace(startingpath, "")

            if itemparent != "":
                itemparent = itemparent.replace('/','')
                itemparent += "/"

            itemname = itemparent + item.name
            filenames.append(itemname)
        elif item.is_dir():
            print("Directory!")

    # for name in glob.glob(startingpath + "/**/*", recursive=True):


        # print(name)
        # filenames.append(name.replace(startingpath,""))

    return filenames

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

    # Patched 060823 to reflect new pathname
    rootpath = "/opt/lampp/htdocs/basicbiologydb/BasicBiologyDatabase/";

    # Get list of personid/documentfilepath tuples
    person_documentdirs = get_people_with_document_directories()

    # Knock out any directories that don't exist
    check_documentdirs(person_documentdirs, rootpath)

    # For each user with a document filepath
    for person_documentdir in person_documentdirs:

        personid = person_documentdir[0]
        personlastname = person_documentdir[1]
        personfirstname = person_documentdir[2]
        persondocpath = person_documentdir[3]

        # Get list of user documents from database
        personfilesfromdb = get_person_documents_from_db(personid)

        # Get list of user documents from document share path
        personfilesfromdirectory = gettreewalkedfilenames(persondocpath, rootpath)

        # Compare the two collections
        databaseupdates = comparefilelists(personfilesfromdb, personfilesfromdirectory)

        # Update database
        updatedatabase(personid, personlastname, personfirstname, databaseupdates)

    # mydb = mysql.connector.connect(
    #   host="localhost",
    #   user="root",
    #   password="",
    #   database="biologydb"
    # )
    # mycursor = mydb.cursor()
    #
    # sql = "insert into data_person_documents (personid, documenttypeid, filename) values (171, 1, 'filename')"
    #
    # mycursor.execute(sql)
    #
    # mydb.commit()
    #
    # print(mycursor.rowcount, "record(s) affected")


    # mycursor.execute("SELECT * FROM code_countries")
    #
    # myresult = mycursor.fetchall()
    #
    # for x in myresult:
    #     print(x)


from flask import Flask, Response

app = Flask(__name__)

# بيانات تجريبية (ممكن تستبدلها بسحب بيانات من SQL أو Active Directory)
database = {
    "IT": [
        {"name": "Ahmed Ali", "number": "1001"},
        {"name": "Maged Saeed", "number": "1002"}
    ],
    "HR": [
        {"name": "Sara Omar", "number": "2001"},
        {"name": "Laila Helmy", "number": "2002"}
    ]
}

# 1. الصفحة الرئيسية (قائمة الأقسام)
@app.route('/directory')
def main_menu():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <CiscoIPPhoneMenu>
        <Title>Groups Directory</Title>
        <Prompt>Choose a Department</Prompt>"""
    
    for dept in database.keys():
        xml += f"""
        <MenuItem>
            <Name>{dept} Department</Name>
            <URL>http://[YOUR_SERVER_IP]:5000/directory/{dept}</URL>
        </MenuItem>"""
    
    xml += "\n</CiscoIPPhoneMenu>"
    return Response(xml, mimetype='text/xml')

# 2. صفحة الأسماء داخل كل قسم
@app.route('/directory/<dept_name>')
def show_dept(dept_name):
    contacts = database.get(dept_name, [])
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <CiscoIPPhoneDirectory>
        <Title>{dept_name} Contacts</Title>
        <Prompt>Select to Dial</Prompt>"""
    
    for person in contacts:
        xml += f"""
        <DirectoryEntry>
            <Name>{person['name']}</Name>
            <Telephone>{person['number']}</Telephone>
        </DirectoryEntry>"""
    
    xml += "\n</CiscoIPPhoneDirectory>"
    return Response(xml, mimetype='text/xml')

if __name__ == '__main__':
    # تأكد من وضع IP الجهاز اللي شغال عليه الكود
    app.run(host='0.0.0.0', port=5000)

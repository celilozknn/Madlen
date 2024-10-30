from bs4 import BeautifulSoup as bs

with open("madlen.html", "r") as madlen:
    content = madlen.read()

soup = bs(content, "html.parser") # Don't know what's lxml
print(soup.prettify())
tag_5 = soup.find("h5") # Find gives the first one
courses_name_tags_h5 = soup.find_all("h5") 
print(courses_name_tags_h5)
print(tag_5)
print()

courses_name = []
for course_name_tag in courses_name_tags_h5:
    courses_name.append(course_name_tag.text)
#print(courses_name)

courses_tags = soup.find_all("section", class_= "course") # class is a keyword for python

courses = []
for course in courses_tags:
    # courses.append(course.h5) # tags with h5
    course_name = course.h5.text
    course_desc = course.p.text
    course_price = course.a.text.split(" ")[-1] # last part of the text is price
    print(course_name)
    print(course_desc)
    print(course_price)
    print(f"{course_name} costs {course_price} dollars.")
    print()





"""price_tags = soup.find_all("a", href= True)
for price in price_tags:
    print(price.text)"""

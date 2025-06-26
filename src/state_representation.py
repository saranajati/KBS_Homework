
class Person:
    def __init__(self, name, speed):
        self.name = name  # اسم الشخص (مثل: "أنت"، "مساعد مختبر" إلخ)
        self.speed = speed  # سرعة الشخص في عبور الجسر (دقائق)
        self.position = "left"  # الموقع الافتراضي هو "يسار"

    def __repr__(self):
        return f"{self.name}({self.speed} min)"


class State:
    def __init__(self, people, lamp_position):
        """
        تمثيل الحالة:
        - people: قائمة من الأشخاص مع سرعاتهم ومواقعهم.
        - lamp_position: يمثل أين يقع المصباح "left" أو "right".
        """
        self.people = people  # قائمة الأشخاص
        self.lamp_position = lamp_position  # "left" أو "right"

    def __repr__(self):
        people_str = ", ".join(
            [f"{person.name}: {person.position}" for person in self.people]
        )
        return f"People: {people_str}, Lamp: {self.lamp_position}"


# اختبار تمثيل الأشخاص والحالة
if __name__ == "__main__":
    # إنشاء الأشخاص مع سرعاتهم
    person1 = Person("أنت", 1)
    person2 = Person("مساعد مختبر", 2)
    person3 = Person("العامل", 5)
    person4 = Person("العالم", 10)

    # تمثيل الحالة الابتدائية
    initial_state = State([person1, person2, person3, person4], "left")

    print(initial_state)
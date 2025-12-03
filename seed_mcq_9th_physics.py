from app import app, db, Course, Assignment
import json
from datetime import datetime

MCQS = [
    {"q":"SI unit of speed is:","options":{"a":"m/s","b":"km/h","c":"m²/s","d":"cm²/s"},"answer":"a"},
    {"q":"A body is said to be in motion when:","options":{"a":"It rotates around itself","b":"Its position changes with respect to surroundings","c":"It vibrates only","d":"None of these"},"answer":"b"},
    {"q":"Which law is called the ‘Law of Inertia’?","options":{"a":"First Law","b":"Second Law","c":"Third Law","d":"Law of Gravitation"},"answer":"a"},
    {"q":"Which of the following is an example of Newton’s Third Law?","options":{"a":"A ball falling under gravity","b":"A gun recoiling when fired","c":"A car accelerating","d":"A body at rest"},"answer":"b"},
    {"q":"Acceleration due to gravity (g) on Earth is approximately:","options":{"a":"8.9 m/s²","b":"9.8 m/s²","c":"10.8 m/s²","d":"98 m/s²"},"answer":"b"},
    {"q":"Free fall is a motion under the influence of:","options":{"a":"Only friction","b":"Only gravity","c":"Gravity and air resistance","d":"Inertia"},"answer":"b"},
    {"q":"Work is said to be done when:","options":{"a":"Force is applied and body does not move","b":"Force is applied and displacement takes place","c":"No displacement occurs","d":"Force is perpendicular to displacement"},"answer":"b"},
    {"q":"SI unit of energy is:","options":{"a":"Joule","b":"Watt","c":"Newton","d":"Pascal"},"answer":"a"},
    {"q":"Sound cannot travel through:","options":{"a":"Solids","b":"Liquids","c":"Gases","d":"Vacuum"},"answer":"d"},
    {"q":"The pitch of a sound depends on its:","options":{"a":"Amplitude","b":"Frequency","c":"Velocity","d":"Intensity"},"answer":"b"},
    {"q":"The angle of incidence is equal to the angle of reflection. This is:","options":{"a":"Law of Refraction","b":"Law of Reflection","c":"Snell’s Law","d":"Fermat’s Law"},"answer":"b"},
    {"q":"Bending of light when it enters from air to water is called:","options":{"a":"Reflection","b":"Diffraction","c":"Refraction","d":"Dispersion"},"answer":"c"},
    {"q":"SI unit of pressure is:","options":{"a":"Watt","b":"Pascal","c":"Newton","d":"Joule"},"answer":"b"},
    {"q":"Hydraulic brakes in vehicles work on:","options":{"a":"Newton’s First Law","b":"Law of Gravitation","c":"Pascal’s Law","d":"Archimedes’ Principle"},"answer":"c"},
    {"q":"SI unit of temperature is:","options":{"a":"Fahrenheit","b":"Celsius","c":"Kelvin","d":"Joule"},"answer":"c"},
    {"q":"Heat is a form of:","options":{"a":"Work","b":"Energy","c":"Force","d":"Pressure"},"answer":"b"},
    {"q":"Friction always acts:","options":{"a":"In the direction of motion","b":"Opposite to the direction of motion","c":"At right angles to motion","d":"In any random direction"},"answer":"b"},
    {"q":"Which reduces friction?","options":{"a":"Rough surface","b":"Oil lubrication","c":"Increasing weight","d":"Dry contact"},"answer":"b"},
    {"q":"The SI unit of electric current is:","options":{"a":"Ampere","b":"Coulomb","c":"Volt","d":"Ohm"},"answer":"a"},
    {"q":"Which of the following is a good conductor of electricity?","options":{"a":"Wood","b":"Rubber","c":"Copper","d":"Glass"},"answer":"c"},
    {"q":"Displacement is a ______ quantity.","options":{"a":"Scalar","b":"Vector","c":"Both","d":"None"},"answer":"b"},
    {"q":"Which law defines force as mass × acceleration?","options":{"a":"Newton’s First Law","b":"Newton’s Second Law","c":"Newton’s Third Law","d":"Archimedes’ Law"},"answer":"b"},
    {"q":"Weight of an object on the Moon is:","options":{"a":"Same as Earth","b":"1/6th of Earth","c":"6 times Earth","d":"Zero"},"answer":"b"},
    {"q":"1 Watt = ?","options":{"a":"1 Joule/second","b":"1 Joule × second","c":"1 Newton/second","d":"1 Coulomb/second"},"answer":"a"},
    {"q":"Sound waves are:","options":{"a":"Longitudinal","b":"Transverse","c":"Electromagnetic","d":"Polarized"},"answer":"a"},
    {"q":"The mirror used in rear-view mirrors of cars is:","options":{"a":"Concave","b":"Convex","c":"Plane","d":"None"},"answer":"b"},
    {"q":"Buoyant force acts:","options":{"a":"Downward","b":"Upward","c":"Sideways","d":"Randomly"},"answer":"b"},
    {"q":"Heat transfer by direct contact is called:","options":{"a":"Radiation","b":"Conduction","c":"Convection","d":"Evaporation"},"answer":"b"},
    {"q":"Unit of friction is the same as:","options":{"a":"Pressure","b":"Work","c":"Force","d":"Energy"},"answer":"c"},
    {"q":"Which device measures electric current?","options":{"a":"Voltmeter","b":"Ammeter","c":"Galvanometer","d":"Ohmmeter"},"answer":"b"}
]

if __name__ == "__main__":
    with app.app_context():
        course = Course.query.filter_by(class_level='9th', subject='Physics').first()
        if not course:
            print("9th Physics course not found.")
        else:
            title = '9th Class Physics – 30 MCQs'
            assignment = Assignment.query.filter_by(course_id=course.id, title=title).first()
            payload = json.dumps(MCQS)
            if not assignment:
                assignment = Assignment(course_id=course.id, title=title, description='Multiple Choice Questions for 9th Class Physics', questions=payload, created_at=datetime.utcnow())
                db.session.add(assignment)
                action = 'created'
            else:
                assignment.questions = payload
                assignment.description = 'Multiple Choice Questions for 9th Class Physics'
                action = 'updated'
            db.session.commit()
            print(f"MCQ assignment {action} for course {course.name} (id={course.id})")

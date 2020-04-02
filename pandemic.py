import uuid
import random
from math import sqrt
from numpy.random import normal
import matplotlib.pyplot as plt

# MODEL PARAMETERS
N_population = 10 # number of people
x_size = 2  # x dimension of area in km
y_size = 2  # y dimension of area in km
dv = 0.05 # mean of person's velocity
mobile_ratio = 1 # ratio of mobile persons
death_ratio = 0.03 # death ratio
starting_infected_ratio = 0.4 # infected ratio at the beginning
dt = 1 # timestep in hours
simulation_time = 10000 # simulation time
incubation_time = 120 # mean of incubation time
recovery_time = 500 # recovery time
min_contact_time = 3 # minimum contact time required for infection
min_contact_distance = 0.5 # minimum contact distance required for infection

#state: healthy, infected, ill, recovered, dead
class Contact:
    def __init__(self, id, state):
        self.id = id # id of other person
        self.state = state
        self.time = 0 # time of contact


class Person:
    def __init__(self, x, y, state):
        self.x = x
        self.y = y
        self.__state = state
        self.infection_time = 0
        self.illness_time = 0
        self.mobile = False
        self.id = uuid.uuid4() # generate unique id
        self.contacts = [] # list of every contact with other people
    def __eq__(self, other):
        return self.id == other.id
    def SetState(self, state):
        self.state = state
    def GetState(self):
        return self.state
    def Move(self):
        if self.mobile and self.state != 'ill':
            dx = normal()*dv
            dy = normal()*dv
            self.x += dx
            self.y += dy
            # boundary conditions
            self.x = (self.x + x_size) % x_size
            self.y = (self.y + y_size) % y_size

    def UpdateContacts(self, nearby_people):
        updated_contacts = []
        for person in nearby_people:
            found = False
            for contact in self.contacts:
                if person.id == contact.id:
                    contact.time += dt
                    contact.state = person.state
                    updated_contacts.append(contact)
                    found = True
            if found == False:
                contact = Contact(person.id, person.state)
                updated_contacts.append(contact)
        self.contacts = updated_contacts[:]

    def UpdateState(self):
        if self.state == 'ill':
            print('chory. czas choroby '+str(self.illness_time))
            if self.illness_time >= recovery_time:
                if random.random() <= death_ratio:
                    self.state = 'dead'
                else:
                    self.state = 'recovered'
            else:
                self.illness_time += dt
        elif self.state == 'infected':
            print('zarażony. czas zarażenia '+str(self.infection_time))
            if self.infection_time >= incubation_time:
                print('wchodze')
                self.state == 'ill'
                self.illness_time = 0
            else:
                self.infection_time += dt
        elif self.state == 'healthy':
            print('jestem zdrowy')
            updated_contacts = []
            for contact in self.contacts:
                if contact.time >= min_contact_time:
                    if contact.state == 'infected' or contact.state == 'ill':
                        self.state = 'infected'
                        self.infection_time = 0
                else:
                    updated_contacts.append(contact)
            self.contacts = updated_contacts[:]


def IsDistanceUnsafe(person1, person2):
    return sqrt((person1.x-person2.x)**2 + (person1.y-person2.y)**2) < min_contact_distance

def SearchForNearbyPeople(current_person, persons):
    nearby_people = []
    for person in persons:
        if IsDistanceUnsafe(current_person, person):
            nearby_people.append(person)
    return nearby_people

def ShowPeopleCoordinates(persons, title):
    states_and_colors = {'healthy': 'green', 'infected': 'blue', 'ill': 'red', 'recovered': 'purple'}
    for key in states_and_colors.keys():
        points_x = []
        points_y = []
        for person in persons:
            if person.state == key:
                points_x.append(person.x)
                points_y.append(person.y)
        plt.plot(points_x, points_y, 'ro', color = states_and_colors[key])
    plt.xlim(0, x_size)
    plt.ylim(0, y_size)
    # plt.ylabel('Liczba schematów')
    # plt.xlabel('Liczba ciągów')
    plt.title(title)
    # plt.savefig('plot_'+str(dlugosc)+'.png')
    plt.show()
    plt.close()


def Populate(infected_ratio, mobile_ratio, n):
    persons = [Person(random.random() * x_size, random.random() * y_size, 'healthy') for i in range(n)]
    for person in persons:
        if random.random() <= infected_ratio:
            person.state = 'infected'
        if random.random() <= mobile_ratio:
            person.mobile = True
    return persons


def Simulate():
    persons = Populate(starting_infected_ratio, mobile_ratio, N_population)
    # plot_moments = [0, 10, 50, 100, 500, 1000, 2000, 3000, ]
    time = 0
    while time <= simulation_time:
        updated_persons = []
        for person in persons:
            person.Move()
            person.UpdateContacts(SearchForNearbyPeople(person, persons))
            person.UpdateState()
            if person.state != 'dead':
                updated_persons.append(person)
        if time % 1000 == 0:
            ShowPeopleCoordinates(persons, str(time))
        persons = updated_persons[:]
        time += dt

Simulate()

# TODO można zrobić kontakty tylko wtedy, kiedy osoba jest zarażona

import uuid
import random
from math import sqrt
from numpy.random import normal
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# MODEL PARAMETERS
N_population = 100 # number of people
x_size = 2  # x dimension of area in km
y_size = 2  # y dimension of area in km
dv = 0.05 # mean of person's velocity
mobile_ratio = 0.5 # ratio of mobile persons
death_ratio = 0.03 # death ratio
starting_infected_ratio = 0.02 # infected ratio at the beginning
dt = 1 # timestep in hours
simulation_time = 3001 # simulation time
incubation_time = 300 # mean of incubation time
recovery_time = 500 # recovery time
min_contact_time = 2 # minimum contact time required for infection
min_contact_distance = 0.05 # minimum contact distance required for infection
medic_ratio = 0.05

#states: healthy, infected, ill, recovered, dead
class Contact:
    def __init__(self, id, state):
        self.id = id # id of other person
        self.state = state
        self.time = 0 # time of contact


class Person:
    def __init__(self, x, y, state):
        self.x = x
        self.y = y
        self.state = state
        self.infection_time = 0
        self.illness_time = 0
        self.mobile = False
        self.medic = False
        self.id = uuid.uuid4() # generate unique id
        self.contacts = [] # list of every contact with other people
    def __eq__(self, other):
        return self.id == other.id
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
            if self.illness_time >= recovery_time:
                if random.random() <= death_ratio:
                    self.state = 'dead'
                else:
                    self.state = 'recovered'
            else:
                self.illness_time += dt
        elif self.state == 'infected':
            if self.infection_time >= incubation_time:
                self.state = 'ill'
                self.illness_time = 0
            else:
                self.infection_time += dt
        elif self.state == 'healthy':
            updated_contacts = []
            for contact in self.contacts:
                if contact.time >= min_contact_time:
                    if (contact.state == 'infected' and self.medic == False) or contact.state == 'ill':
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
    plt.ylabel('y dimension [km]')
    plt.xlabel('x dimension [km]')
    plt.title(title)
    plt.savefig('pop_'+title+'.png')
    plt.close()


class Statistics:
    def __init__(self):
        self.healthy = []
        self.infected = []
        self.ill = []
        self.recovered = []
        self.dead = []
    def AddSample(self, sample : dict):
        self.healthy.append(sample['healthy'])
        self.infected.append(sample['infected'])
        self.ill.append(sample['ill'])
        self.recovered.append(sample['recovered'])
        self.dead.append(sample['dead'])


def ShowPeopleStatistics(statistics, title):
    states_and_colors = {'healthy': 'green', 'infected': 'blue', 'ill': 'red', 'recovered': 'purple', 'dead': 'black'}
    time = [i for i in range(len(statistics.healthy))]
    plt.plot(time, statistics.healthy, color = states_and_colors['healthy'])
    plt.plot(time, statistics.infected, color = states_and_colors['infected'])
    plt.plot(time, statistics.ill, color = states_and_colors['ill'])
    plt.plot(time, statistics.recovered, color = states_and_colors['recovered'])
    plt.plot(time, statistics.dead, color = states_and_colors['dead'])
    plt.ylabel('Population')
    plt.xlabel('Time [hours]')
    patches = [mpatches.Patch(color = item, label = key) for key, item in states_and_colors.items()]
    plt.legend(handles = patches)
    plt.title(title)
    plt.savefig('stats_'+title+'.png')
    plt.close()


def Populate(infected_ratio, mobile_ratio, n):
    persons = [Person(random.random() * x_size, random.random() * y_size, 'healthy') for i in range(n)]
    for person in persons:
        if random.random() <= infected_ratio:
            person.state = 'infected'
        if random.random() <= mobile_ratio:
            person.mobile = True
        if random.random() <= medic_ratio:
            person.medic = True
    return persons


def Simulate():
    persons = Populate(starting_infected_ratio, mobile_ratio, N_population)
    statistics = Statistics()
    time = 0
    while time <= simulation_time:
        sample = {'healthy': 0, 'infected': 0, 'ill': 0, 'recovered': 0, 'dead': 0}
        for person in persons:
            sample[person.state] += 1
            person.Move()
            person.UpdateContacts(SearchForNearbyPeople(person, persons))
            person.UpdateState()
        statistics.AddSample(sample)
        if sample['infected'] + sample['ill']>=0.25*N_population:
            print('zarazone 25% dla chwili: '+str(time))
        if time % 500 == 0:
            ShowPeopleCoordinates(persons, str(time))
            ShowPeopleStatistics(statistics, str(time))
        time += dt

Simulate()

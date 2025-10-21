import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()
random.seed(42)
Faker.seed(42)

# Configuration
NUM_RECORDS = 500 # Some pts will have multiple appts
NUM_UNIQUE_PTS = 350
current_date = datetime.now()

# Define lists for categorical data
statuses = [
    'New Patient',
    'Needs Reschedule',
    'Pt Cancelled',
    'Hosp Cancelled',
    'Confirmed',
    'Completed',
    'Awaiting Callback'
]

appt_types = [
    'Initial Consult',
    'Follow-Up',
    'Procedure',
    'Surgery',
    'Lab Work',
    'Imaging',
    'Physical Therapy',
    'Annual Check-Up'
]

depts = [
    'Cardiology',
    'Orthopedics',
    'PCP',
    'Neurology',
    'GI',
    'Dermatology',
    'ENT',
    'Physical Therapy',
    'Radiology'
]

priority_levels = ['High', 'Medium', 'Low']

# Fixed list of Provider names
providers = [
    'Dr. Camille Haberman',
    'Dr. Everly Prosienski',
    'Dr. Hope Santano',
    'Dr. Gerardo Tarwater',
    'Dr. Michael Rorex',
    'Dr. Dominic Schnorr',
    'Dr. Aurora Dildine',
    'Dr. Juliana Simlick',
    'Dr. Kai Mecca',
    'Dr. Amir Hilty',
    'Dr. Beverly Thorsen',
    'Dr. Hadley Cogan',
    'Dr. Riley Beyal',
    'Dr. Caden Santoli',
    'Dr. Catherine Rosenkranz',
    'Dr. Carson Borras',
    'Dr. Julia Slaton',
    'Dr. Thelma Tellers',
    'Dr. Heaven Darring',
    'Dr. Aidan Latiolais'
]

# Fixed list of Hospitals/Facilities
hospitals = [
    'Wellness General Hospital',
    'Rose Valley Clinic',
    'Summerhill Medical Center',
    'Rose Gardens Medical Clinic',
    'Peace Forest Medical Clinic',
    'Grand Meadow Clinic',
    'Spring Forest Clinic',
    'Flowerhill Medical Clinic',
    'Great Plains General Hospital',
    'Blossomvale Hospital'
]

agents = [
    'Sarah Johnson',
    'Michael Chen',
    'Jessica Rodriguez',
    'David Kim',
    'Emily Watson',
    'Christopher Lee',
    'Amanda Martinez',
    'Cael Hobbs',
    'Dominic Wallace',
    'Blake Gallagher',
    'Lexie Edwards',
    'Hannah Newman',
    'Luciana Marti',
    'Dylan Valerio',
    'Mary MacDarcy'
]

cancel_reasons = [
    'Scheduling Conflict',
    'Pt No Show',
    'Pt Sick',
    'Transportation',
    'Weather'
    'Feeling Better',
    'Insurance',
    'Provider Cancellation',
    'Hosp Cancellation',
    'Pt Cancellation',
    'No Reason Given'
]

call_depos = [
    'Appointed',
    'Left VM',
    'No Answer',
    'Callback Requested',
    'Wrong Number',
    'Disconnected',
    'Pt Declined',
    'Hung Up',
    'DNC',
    'Reconfirmed'
]

agent_statuses = [
    'Available',
    'On Call',
    'Wrap-Up',
    'Break',
    'Lunch',
    'Meeting',
    'Training'
]

# Generate base pt pool
base_pts = []
for i in range(NUM_UNIQUE_PTS):
    base_pts.append({
        'pt_id': f'PT{1000 + 1}',
        'pt_name': fake.name(),
        'phone': fake.phone_number(),
        'dob': fake.date_of_birth(minimum_age=18, maximum_age=85)
    })

# Create appt journey mapping
appt_journey = [
    'Initial Consult': ['Follow-Up','Procedure','Lab Work','Imaging'],
    'Follow-Up': ['Procedure','Surgery','Lab Work','Imaging','Follow-Up'],
    'Procedure': ['Follow-Up'],
    'Surgery': ['Follow-Up','Physical Therapy'],
    'Lab Work': ['Follow-Up'],
    'Imaging': ['Follow-Up'],
    'Physical Therapy': ['Follow-Up','Physical Therapy'],
    'Annual Check-Up': ['Lab Work','Follow-Up']
]

# Generate dataset with pt histories
data = []
pt_history = {} # Track what appts each pt has had

# First pass: Create initial appts for most pts
for i in range(NUM_UNIQUE_PTS):
    pt = base_pts[i]

    # Random initial appt type
    initial_appt_types = ['Initial Consult','Annual Check-Up','Follow-Up']
    appt_type = random.choice(initial_appt_types)

    # Store this pt's first appt
    pt_history[pt['pt_id']] = [appt_type]

    record = generate_appt_record(
        pt, appt_type, current_date, is_return_visit=False
    )
    data.append(record)

# Second pass: Add return visits for some pts
remaining_records = NUM_RECORDS - NUM_UNIQUE_PTS
return_visit_pts = random.sample(base_pts, min(remaining_records, NUM_UNIQUE_PTS))

for pt in return_visit_pts[:remaining_records]:
    # Get pts's previous appt type
    previous_appts = pt_history[pt['pt_id']]
    last_appt = previous_appts[-1]

    # Determine next logical appt type
    if last_appt in appt_journey:
        possible_next = appt_journey[last_appt]
        next_appt_type = random.choice(possible_next)
    else:
        next_appt_type = 'Follow-Up'

    # Store this appt
    pt_history[pt['pt_id']].append(next_appt_type)

    record = generate_appt_record(
        pt, next_appt_type, current_date, is_return_visit=True,
        visit_number=len(pt_history[pt['pt_id']])
    )
    data.append(record)

def generate_appt_record(pt, appt_type, current_date, is_return_visit=False, visit_number=1):
    """Generate a single appt record for a pt"""

    dept = random.choice(depts)
    provider = random.choice(providers)
    hosp = random.choice(hospitals)

    # Determine status with weights
    if is_return_visit:
        # Return visits more likely to be confirmed/completed
        status_weights = [0.08, 0.10, 0.05, 0.03, 0.40, 0.30, 0.04]
    else:
        # New pts more likely to need initial scheduling
        status_weights = [0.20, 0.22, 0.08, 0.05, 0.30, 0.20, 0.05]

    status = random.choices(statuses, weight=status_weights)[0]

    # Priority based on appt type and rating
    if appt_type in ['Surgery','Procedure'] or status == 'New Patient':
        priority = random.choices(priority_levels, weights=[0.5, 0.3, 0.2])[0]
    elif appt_type == 'Annual Check-Up':
        priority = random.choices(priority_levels, weights=[0.05, 0.25, 0.7])[0]
    else:
        priority = random.choice(priority_levels, weights=[0.2, 0.5, 0.3])[0]

    # Calculate days since last contact based on priority and outlier distribution
    outlier_chance = random.random()

    if priority == 'High':
        if outlier_chance < 0.10:
            days_since_contact = random.randint(8, 21)
        elif outlier_chance < 0.25:
            days_since_contact = random.randint(2, 4):
        else:
            days_since_contact = random.randint(0, 1)
    elif priority == 'Medium':
        if outlier_chance < 0.08:
            days_since_contact = random.randint(8, 18)
        elif outlier_chance < 0.23:
            days_since_contact = random.randint(4, 7)
        else:
            days_since_contact = random.randint(0, 3)
    else:
        if outlier_chance < 0.05:
            days_since_contact = random.randint(10, 25)
        elif outlier_chance < 0.20:
            days_since_contact = random.randint(5, 9)
        else:
            days_since_contact = random.randint(0, 5)

    last_contact_date = current_date - timedelta(days=days_since_contact)

    # Contact attempts correlate with days since contact
    if days_since_contact > 10:
        contact_attempts = random.randint(4, 8)
    elif days_since_contact > 5:
        contact_attempts = random.randint(2, 4)
    else:
        contact_attempts = random.randint(0, 2)

    # Date referred (before last contact)
    if is_return_visit:
        # Return visits are recent referrals
        days_since_referral = days_since_contact + random.randint(1, 14)
    else:
        days_since_referral = days_since_contact + random.randint(1, 30)

    referral_date = current_date - timedelta(date_since_referral)

    # Call disposition and agent info
    if status in ['Confirmed','Completed']:
        call_disposition = 'Appointed'
        agent_name = random.choice(agents)
        agent_status = random.choice(['Available','Wrap-Up'])
    elif status == 'Awaiting Callback':
        call_disposition = random.choice(['Left VM','Callback Requested'])
        agent_name = random.choice(agents)
        agent_status = 'Wrap-Up'
    elif contact_attempts > 0:
        call_disposition = random.choice(['Left VM','No Answer','Wrong Number'])
        agent_name = random.choice(agents)
        agent_status = random.choice(['Available','Wrap-Up','On Call'])
    else:
        call_disposition = None
        agent_name = None
        agent_status = None

    # Scheduled information
    scheduled_by = random.choice(agents) if status in ['Confirmed','Completed'] else None

    if status == 'Completed'
        date_scheduled = fake.date_time_between(start_date='-90d', end_date='-7d')
        appt_date = fake.date_time_between(start_date=date_scheduled, end_date='now')

        # Call metrics for completed calls
        call_duration = random.randint(3, 15)
        wrap_up_duration = random.randint(1, 5)
        handle_time = call_duration + wrap_up_duration
        first_call_resolution = random.choice([True, True, True, False]) #75% FCR

        time_to_schedule = (date_scheduled - referral_date).days
    elif status == 'Confirmed'
        date_scheduled = fake.date_time_between(start_date=referral_date, end_date='now')
        appt_date = fake.date_time_between(start_date='now', end_date='+90d')

        call_duration = random.randint(3, 15)
        wrap_up_duration = random.randint(1, 5)
        handle_time = call_duration + wrap_up_duration
        first_call_resolution = random.choice([True, True, True, False])

        time_to_schedule = (date_scheduled - referral_date).days
    else:
        date_scheduled = None
        appt_date = None
        call_duration = None
        wrap_up_duration = None
        handle_time = None
        first_call_resolution = None
        time_to_schedule = None

    # Load time
    if appt_date and date_scheduled:
        load_time = (appt_date - date_scheduled).days
    else:
        load_time = None

    # Reason/notes based on status
    if status in ['Pt Cancelled','Hosp Cancelled']:
        reason = random.choice(cancellation_reasons)
        notes = f'Cancelled: {reason}'
    elif status == 'Needs Reschedule':
        reason = random.choice(cancellation_reasons[:5])
        notes = f'Reschedule Needed: {reason}'
    elif status == 'Awaiting Callback':
        notes = 'Left VM, awaiting callback'
    elif contact_attempts > 3:
        notes = f'Multiple contact attempts ({contact_attempts}), no response'
    elif is_return_visit:
        notes = f'Return visit (Visit #{visit_number})'
    else:
        notes = ''

    # Insurance type
    insurance_type = random.choice(
        ['Commercial','Medicaid','Medicare','Self-Pay'],
        weights=[0.50, 0.25, 0.15, 0.10]
    )[0]

    # Referral_source
    if is_return_visit:
        referral_source = 'Follow-Up Care'
    else:
        referral_source = random.choice(['Primary Care','Specialist','ER','Self-Referral'])

    return {
        'patientId': pt['pt_id'],
        'patientName': pt['pt_name'],
        'dob': pt['dob'].strftime('%m/%d/%Y')
        'phoneNumber': pt['phone'],
        'department': dept,
        'doctor': provider,
        'facility': hosp,
        'apptType': appt_type,
        'status': status,
        'priorityLevel': priority,
        'referralDate': referral_date.strftime('%m/%d/%Y')
        'referralSource': referral_source,
        'lastContactDate': last_contact_date.strftime('%m/%d/%Y'),
        'daysSinceLastContact': days_since_contact,
        'contactAttempts': contact_attempts,
        'callDisposition': call_disposition,
        'agentName': agent_name,
        'agentStatus': agent_status,
        'scheduledBy': scheduled_by,
        'dateScheduled': date_scheduled.strftime('%m/%d/%Y') if date_scheduled else None,
        'apptDate': appt_date.strftime('%m/%d/%Y') if appt_date else None
        'callDurationMin': call_duration,
        'wrapUpDurationMin': wrap_up_duration,
        'firstCallResolution': first_call_resolution,
        'timetoScheduleDays': time_to_schedule,
        'leadTimeDays': ;ead_time,
        'insuranceType': insurance_type,
        'visitNumber': visit_number,
        'isReturnVisit': is_return_visit,
        'notes': notes
    }

# Create DataFrame
df = pd.DataFrame(data)

# Sort by patientID and referralDate to show pt journey
df = df.sort_values(['patientId','referralDate'])

# Export to CSV
df.to_csv('pt_scheduling_data.csv', index=False)

print(f'Dataset created successfully with {NUM_RECORDS} records!')
print(f'Unique pts: {NUM_UNIQUE_PTS}')
print(f'Pts with multiple visits: {NUM_RECORDS - NUM_UNIQUE_PTS}')
print(f'\nDataset saved as: pt_scheduling_data.csv')
print(f'\nStatus Distribution:')
print(df['status'].value_counts())
print(f'\nPriority Distribution:')
print(df['priorityLevel'].value_counts())
print(f'\nReturn Visit Distribution:')
print(df['isReturnVisit'].value_counts())
print(f'\nDoctor with Most Patients:')
print(df['doctor'].value_counts())
print(f'\nPatients with Multiple Appts (Sample):')
multi_visit = df[df['patientId'].duplicated(keep=False)].groupby('patientId').size().sort_values(ascending=False)
print(multi_visit.head(10))
print(f'\nOutliers (Days Since Last Contact > 7):')
print(df[df['daysSinceLastContact'] > 7][['patientName','priorityLevel','daysSinceLastContact','status','isReturnVisit']].head(10))

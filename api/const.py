import os

from mongoengine import connect, DynamicDocument

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = int(os.environ.get('DB_PORT'))
DB_SSL = os.environ.get('DB_SSL') == "True"
REPLICA_SET = os.environ.get('DB_REPLICA_SET', None)

def connect_db():
    connect(
        db=DB_NAME,
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        ssl=DB_SSL,
        replicaset=REPLICA_SET,
        authentication_source='admin'
    )


categorical_columns = ["JS-gender", "JS-highest_edu_level", "JS-nationality", "JS-gendermix_not_allowed", "JS-benefit1", "JS-benefit2", "JS-english_proficiency", "JS-impairments", "JS-major", "JS-opposite_gender_coworkers", "JS-opposite_gender_manager", "JS-first_job_field_preference", "JS-second_job_field_preference", "JOB-bus_covered", "JOB-childcare_subsidy_offered", "JOB-dorm_covered", "JOB-driving_ability_required", "JOB-education_required", "JOB-english_proficiency_required", "JOB-female_requied", "JOB-free_meals_at_wok", "JOB-health_insurance_offered", "JOB-hearing_disability_accepted", "JOB-housing_subsidy_offered", "JOB-it_proficiency_required", "JOB-job_category", "JOB-job_description", "JOB-job_production", "JOB-jordanian_experience_required", "JOB-literacy_required", "JOB-male_required", "JOB-meal_subsidy_offered", "JOB-night_shifts_required", "JOB-noncognitive_skill_preference1", "JOB-noncognitive_skill_preference2", "JOB-numeracy_requied", "JOB-physical_disability_accepted", "JOB-physical_work_abilities_required", "JOB-problem_solving_required", "JOB-school_subsidy_offered", "JOB-specialization_required", "JOB-speech_disability_accepted", "JOB-syrian_considered", "JOB-transport_subsidy_offered", "JOB-visual_disability_accepted", "JOB-work_permit_offered",]
all_columns = ["JS-age", "JS-gender", "JS-highest_edu_level", "JS-will_work_night_shift", "JS-nationality", "JS-gendermix_not_allowed", "JS-will_work_qiz",  "JS-benefit1", "JS-benefit2", "JS-daily_hours_willing_to_work", "JS-days_willing_train_unpaid", "JS-distance_willing_to_travel", "JS-english_proficiency", "JS-experience_clerical_work", "JS-experience_factory", "JS-experience_management_work", "JS-experience_manual_labor", "JS-experience_professional_work", "JS-follow_up_agreement", "JS-impairments", "JS-major", "JS-nonarab_coworkers", "JS-opposite_gender_coworkers", "JS-opposite_gender_manager", "JS-weekly_days_willing_to_work", "JS-will_live_in_dorm", "JS-will_train_unpaid", "JS-years_education", "JS-years_exp", "JS-first_job_field_preference", "JS-rwage1", "JS-second_job_field_preference", "JOB-bus_covered", "JOB-childcare_subsidy_offered", "JOB-dorm_covered", "JOB-driving_ability_required", "JOB-education_required", "JOB-english_proficiency_required", "JOB-female_requied", "JOB-free_meals_at_wok", "JOB-health_insurance_offered", "JOB-hearing_disability_accepted", "JOB-housing_subsidy_offered", "JOB-it_proficiency_required", "JOB-job_category", "JOB-job_description", "JOB-job_production", "JOB-jordanian_experience_required", "JOB-literacy_required", "JOB-male_required", "JOB-meal_subsidy_offered", "JOB-night_shifts_required", "JOB-noncognitive_skill_preference1", "JOB-noncognitive_skill_preference2", "JOB-numeracy_requied", "JOB-physical_disability_accepted", "JOB-physical_work_abilities_required", "JOB-problem_solving_required", "JOB-school_subsidy_offered", "JOB-specialization_required", "JOB-speech_disability_accepted", "JOB-syrian_considered", "JOB-transport_subsidy_offered", "JOB-visual_disability_accepted", "JOB-wage_offered", "JOB-work_permit_offered", "JOB-years_experience_required", 'hired_yes_no', 'quit', 'fired']
scalar_columns = ["JS-age", "JS-daily_hours_willing_to_work", "JS-days_willing_train_unpaid", "JS-distance_willing_to_travel", "JS-years_education", "JS-years_exp", "JS-rwage1", "JS-num_children", "JS-personal_income", "JOB-wage_offered"]



use crate::models::{Room, Activity};
use axum_responses::{Result, http::HttpResponse};


fn simultaneus_activities_in_timeslot(timeslot: u32, activities: Vec<Activity>) -> u16 {

    let mut count = 0;

    for activity in activities {
        if activity.time_slots.contains(&timeslot) {
            count += 1;
        }
    }

    count
}


fn max_simultaneus_activities(activities: &Vec<Activity>) -> u16 {
    let mut max_count = 0;

    let mut time_slots_readys: Vec<u32> = Vec::new();

    for activity in activities {
        for time_slot in activity.time_slots.clone() {
            if time_slots_readys.contains(&time_slot) {
                continue;
            }

            let count = simultaneus_activities_in_timeslot(time_slot, activities.clone());

            if count > max_count {
                max_count = count;
            }
            time_slots_readys.push(time_slot);
        }
    }

    max_count
}


fn sort_activities(activities: Vec<Activity>) -> Vec<Activity> {
    let mut sorted_activities = activities;
    sorted_activities.sort_by(|a, b| a.students_count.cmp(&b.students_count));

    sorted_activities
}


fn distance(x1: u32, x0: u32) -> u32 {
    if x1 > x0 { x1 - x0 } else { x0 - x1 }
}


fn get_best_room(activity: Activity, rooms: Vec<Room>) -> Room {
    rooms.into_iter()
        .min_by_key(|r| distance(r.capacity, activity.students_count))
        .unwrap()
}

fn pop_activity(activities: &mut Vec<Activity>) -> Result<Activity> {
    Ok(match activities.pop() {
        Some(a) => a,
        None => return Err(HttpResponse::InternalServerError().error("Failed to pop activity from the list.")),
    })
}


pub fn run_scheduler(mut activities: Vec<Activity>, rooms: Vec<Room>) -> Result<(Vec<Activity>, Vec<Activity>)> {
    println!("Running the scheduling algorithm...");

    // Sort activities by number of students (asending)
    activities = sort_activities(activities.clone());

    let max_simultaneus = max_simultaneus_activities(&activities);
    
    if rooms.len() < max_simultaneus as usize {
        println!("Not enough rooms to schedule all activities.");
        return Err(HttpResponse::BadRequest().error("Not enough rooms to schedule all activities."));
    }

    let mut free_rooms = rooms.clone();

    let mut scheduled_activities: Vec<Activity> = Vec::new();
    let mut unscheduled_activities: Vec<Activity> = Vec::new();

    let mut started_activities: Vec<Activity> = Vec::new();

    let mut current_time_slot = 0;

    while !activities.is_empty() {
        println!("Scheduling activities for time slot {}...", current_time_slot);
        let mut activities_start_in_time_slot: Vec<Activity> = activities
            .clone()
            .into_iter()
            .filter(|a| a.time_slots[0] == current_time_slot)
            .collect();

        if activities_start_in_time_slot.is_empty() && started_activities.is_empty() {
            current_time_slot += 1;
            continue;
        }

        for activity in started_activities.clone() {
            if !activity.time_slots.ends_with(&[current_time_slot - 1]) { // si la actividad no ha terminado
                continue;
            }
            free_rooms.push(activity.room.clone());
            started_activities.retain(|a| a.id != activity.id);
            activities.retain(|a| a.id != activity.id);
        }

        while !activities_start_in_time_slot.is_empty() {
            let mut activity = pop_activity(&mut activities_start_in_time_slot)?;

            let available_rooms: Vec<Room> = free_rooms.clone()
                .into_iter()
                .filter(|r| r.capacity >= activity.students_count)
                .collect();

            if available_rooms.is_empty() {
                println!(
                    "No available rooms for activity {} in time slot {}.",
                    activity.subject, current_time_slot
                );
                unscheduled_activities.push(activity);
                continue;
            }

            let best_room = get_best_room(activity.clone(), available_rooms);

            println!("Assigning activity {} to room {} in time slot {}.", activity.subject, best_room.name, current_time_slot);

            free_rooms.retain(|r| r.name != best_room.name);

            activity.room = best_room;
            started_activities.push(activity.clone());
            scheduled_activities.push(activity);

        }

        current_time_slot += 1;
    }

    Ok((scheduled_activities, unscheduled_activities))
}
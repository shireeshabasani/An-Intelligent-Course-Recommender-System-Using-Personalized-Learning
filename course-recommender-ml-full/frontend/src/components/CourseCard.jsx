import React from 'react';

const CourseCard = ({ course }) => {
  return (
    <div className="course-card">
      <h3>{course.title}</h3>
      <p><strong>Provider:</strong> {course.provider}</p>
      <p><strong>Duration:</strong> {course.duration_hours} hrs</p>
      <p><strong>Price:</strong> ${course.price || 'Free'}</p>
      <a href={course.url} target="_blank" rel="noopener noreferrer" className="btn">Go to Course</a>
    </div>
  );
};

export default CourseCard;

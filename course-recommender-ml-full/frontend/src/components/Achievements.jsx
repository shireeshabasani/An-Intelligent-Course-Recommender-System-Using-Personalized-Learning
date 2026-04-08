
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = 'http://localhost:8000';

const Achievements = ({ user }) => {
    const [quizResults, setQuizResults] = useState([]);
    const [streak, setStreak] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!user?.email) return;
        const fetchData = async () => {
            try {
                const email = encodeURIComponent(user.email);
                const [actRes, quizRes] = await Promise.all([
                    axios.get(`${BACKEND_URL}/users/${email}/activity`),
                    axios.get(`${BACKEND_URL}/users/${email}/quiz-results`)
                ]);
                setStreak(actRes.data.streak || 0);
                setQuizResults(quizRes.data || []);
            } catch (err) {
                console.error("Fetch error", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [user]);

    if (loading) return (
        <div style={{ padding: '100px', textAlign: 'center', fontFamily: 'sans-serif' }}>
            <h2>Loading academic records...</h2>
        </div>
    );

    return (
        <div style={{ padding: '40px 20px', maxWidth: '1000px', margin: '0 auto', fontFamily: '"Segoe UI", Tahoma, sans-serif', backgroundColor: '#F9FAFB', minHeight: '100vh' }}>
            <h2 style={{ color: '#1A202C', borderBottom: '4px solid #38A169', paddingBottom: '15px', marginBottom: '30px' }}>
                🎓 Academic Achievements
            </h2>
            
            <div style={{ display: 'flex', gap: '25px', marginBottom: '40px' }}>
                <div style={{ padding: '25px', background: '#fff', borderRadius: '15px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', flex: 1, textAlign: 'center', borderTop: '5px solid #E53E3E' }}>
                    <div style={{ fontSize: '0.85rem', color: '#718096', fontWeight: 'bold', textTransform: 'uppercase' }}>Daily Streak</div>
                    <div style={{ fontSize: '2.2rem', marginTop: '10px', color: '#2D3748' }}>🔥 {streak} Days</div>
                </div>
                <div style={{ padding: '25px', background: '#fff', borderRadius: '15px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', flex: 1, textAlign: 'center', borderTop: '5px solid #3182CE' }}>
                    <div style={{ fontSize: '0.85rem', color: '#718096', fontWeight: 'bold', textTransform: 'uppercase' }}>Quizzes Attempted</div>
                    <div style={{ fontSize: '2.2rem', marginTop: '10px', color: '#2D3748' }}>✅ {quizResults.length}</div>
                </div>
            </div>

            <h3 style={{ color: '#4A5568', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                📜 Official Quiz History
            </h3>
            
            <div style={{ background: 'white', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ background: '#EDF2F7', borderBottom: '2px solid #E2E8F0' }}>
                            <th style={{ padding: '18px', textAlign: 'left', color: '#4A5568' }}>Course Name</th>
                            <th style={{ padding: '18px', textAlign: 'left', color: '#4A5568' }}>Level</th>
                            <th style={{ padding: '18px', textAlign: 'left', color: '#4A5568' }}>Final Score</th>
                            <th style={{ padding: '18px', textAlign: 'left', color: '#4A5568' }}>Status</th>
                            <th style={{ padding: '18px', textAlign: 'left', color: '#4A5568' }}>Date Completed</th>
                        </tr>
                    </thead>
                    <tbody>
                        {quizResults.length > 0 ? quizResults.map((r, i) => {
                            // THE FIX: Use the 'passed' boolean directly from backend
                            const isPassed = r.passed; 

                            return (
                                <tr key={i} style={{ borderBottom: '1px solid #EDF2F7' }}>
                                    <td style={{ padding: '18px' }}>
                                        <strong style={{ color: '#2D3748' }}>{r.course_title}</strong>
                                    </td>
                                    <td style={{ padding: '18px', color: '#718096' }}>
                                        Level {r.quiz_number}
                                    </td>
                                    <td style={{ padding: '18px', fontWeight: 'bold', color: '#2D3748' }}>
                                        {r.score} / {r.total} 
                                        <span style={{ fontSize: '12px', color: '#A0AEC0', marginLeft: '8px' }}>({r.percentage}%)</span>
                                    </td>
                                    <td style={{ padding: '18px' }}>
                                        <span style={{ 
                                            color: isPassed ? '#22543D' : '#822727', 
                                            backgroundColor: isPassed ? '#C6F6D5' : '#FED7D7',
                                            padding: '6px 14px',
                                            borderRadius: '20px',
                                            fontSize: '0.75rem',
                                            fontWeight: 'bold',
                                            display: 'inline-flex',
                                            alignItems: 'center',
                                            gap: '5px'
                                        }}>
                                            {isPassed ? "PASS ✅" : "FAIL ❌"}
                                        </span>
                                    </td>
                                    <td style={{ padding: '18px', color: '#718096' }}>
                                        {r.completed_at}
                                    </td>
                                </tr>
                            );
                        }) : (
                            <tr>
                                <td colSpan="5" style={{ textAlign: 'center', padding: '50px', color: '#A0AEC0' }}>
                                    No records found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Achievements;
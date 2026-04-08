import React, { useState } from 'react';
import axios from 'axios';

const roles = [ /* your full roles array from earlier */ ];

function SkillQuizPage() {
  const [role, setRole] = useState('');
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  // Fetch quiz on role/skill selection
  const fetchQuiz = async () => {
    if (!role) return;
    const res = await axios.get(`http://127.0.0.1:8000/quiz?role=${encodeURIComponent(role)}`);
    setQuestions(res.data.questions);
    setAnswers({});
    setSubmitted(false);
  };

  const handleSelect = (qIdx, answer) => {
    setAnswers(prev => ({ ...prev, [qIdx]: answer }));
  };

  const grade = questions.reduce((score, q, idx) =>
    score + (answers[idx] === q.answer ? 1 : 0), 0);

  return (
    <div style={{maxWidth:600,margin:'40px auto',padding:24,background:'#fff',borderRadius:8}}>
      <h2>Skill Quiz</h2>
      <select value={role} onChange={e => setRole(e.target.value)} style={{width:'100%',padding:10,fontSize:16,marginBottom:10}}>
        <option value="">Select Role/Skill</option>
        {roles.map(r => <option key={r} value={r}>{r}</option>)}
      </select>
      <button style={{marginBottom:18,padding:'8px 20px'}} onClick={fetchQuiz} disabled={!role}>Start Quiz</button>

      {questions.length > 0 && !submitted && (
        <form onSubmit={e => { e.preventDefault(); setSubmitted(true); }}>
          {questions.map((q, idx) => (
            <div key={idx} style={{marginBottom:18}}>
              <b>{idx+1}. {q.question}</b>
              <div>
                {q.options.map(opt => (
                  <label key={opt} style={{display:'block',margin:'4px 0'}}>
                    <input
                      type="radio"
                      name={`q${idx}`}
                      checked={answers[idx] === opt}
                      onChange={() => handleSelect(idx, opt)}
                      disabled={submitted}
                    />
                    {' '}{opt}
                  </label>
                ))}
              </div>
            </div>
          ))}
          <button type="submit" style={{padding:'8px 22px'}}>Submit Answers</button>
        </form>
      )}

      {submitted && (
        <div style={{marginTop:24}}>
          <h3>Your Score: {grade}/{questions.length}</h3>
          {questions.map((q, idx) => (
            <div key={idx} style={{marginBottom:10}}>
              <b>{idx+1}. {q.question}</b>
              <div>
                <span>Your answer: {answers[idx] || 'Not answered'}</span>
                <br/>
                <span>Correct answer: {q.answer}</span>
                {answers[idx] !== q.answer && q.explanation && (
                  <>
                    <br/>
                    <span style={{color:'darkgreen'}}>Explanation: {q.explanation}</span>
                  </>
                )}
              </div>
            </div>
          ))}
          <button onClick={() => {setQuestions([]); setRole("");}}>Take Another Quiz</button>
        </div>
      )}
    </div>
  );
}

export default SkillQuizPage;

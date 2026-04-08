import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Journey.css'; // See CSS below for the curve

const Journey = ({ user }) => {
  const navigate = useNavigate();
  const maxLevel = user?.max_level || 1;
  const levels = [1, 2, 3, 4, 5, 6, 7];

  return (
    <div className="journey-container">
      {maxLevel > 7 && (
        <div className="congratulations-banner">
          <h1>Congratulations 👑</h1>
          <p>You are now a Master Candidate!</p>
        </div>
      )}

      <div className="path-svg-container">
        {/* Level Nodes */}
        <div className="levels-grid">
          {levels.map((lvl) => (
            <div 
              key={lvl} 
              className={`level-node ${lvl <= maxLevel ? 'unlocked' : 'locked'}`}
              onClick={() => lvl <= maxLevel && navigate(`/journey-quiz/${lvl}`)}
            >
              <div className="icon">
                {lvl < maxLevel ? '✅' : lvl === maxLevel ? '🔓' : '🔒'}
              </div>
              <span>Level {lvl}</span>
            </div>
          ))}
          
          <div className={`level-node master ${maxLevel >= 8 ? 'unlocked' : 'locked'}`}>
            <div className="icon">
            {maxLevel >= 8 ? '👑' : '🔒'}</div>
            <span>Master Level</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Journey;
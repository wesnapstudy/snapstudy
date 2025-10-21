import React, { useState, useEffect } from 'react';
import { Quiz, QuizQuestion, QuizResults as QuizResultsType, User } from '../types';
import { quizService } from '../services/quizService';
import { analyticsService } from '../services/analyticsService';
import QuizResults from './QuizResults';
import './QuizInterface.css';

interface QuizInterfaceProps {
  lessonId: string;
  user: User;
  onQuizComplete?: (results: QuizResultsType) => void;
  onClose?: () => void;
}

const QuizInterface: React.FC<QuizInterfaceProps> = ({ 
  lessonId, 
  user, 
  onQuizComplete, 
  onClose 
}) => {
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [results, setResults] = useState<QuizResultsType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showHint, setShowHint] = useState(false);
  const [hint, setHint] = useState<string | null>(null);
  const [timeSpent, setTimeSpent] = useState(0);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    generateQuiz();
  }, [lessonId]);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(timer);
  }, [startTime]);

  const generateQuiz = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const quizData = await quizService.generateQuiz(lessonId);
      setQuiz(quizData);
      quizService.startQuizTimer();
      
      // Track quiz generation
      await analyticsService.trackEngagementEvent('quiz_generated', {
        quiz_id: quizData.quiz_id,
        lesson_id: lessonId,
        difficulty: quizData.difficulty_level,
        num_questions: quizData.total_questions
      });
      
    } catch (error) {
      console.error('Failed to generate quiz:', error);
      setError('Failed to generate quiz. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId: string, answer: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < (quiz?.questions.length || 0) - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setShowHint(false);
      setHint(null);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
      setShowHint(false);
      setHint(null);
    }
  };

  const handleGetHint = async () => {
    if (!quiz) return;
    
    const currentQuestion = quiz.questions[currentQuestionIndex];
    
    try {
      const hintData = await quizService.getHint(
        quiz.quiz_id,
        currentQuestion.id,
        'Student requested help',
        answers[currentQuestion.id] ? [answers[currentQuestion.id]] : []
      );
      
      setHint(hintData.hint_text || 'Here\'s a hint to help you think about this question.');
      setShowHint(true);
      
      // Track hint request
      await analyticsService.trackEngagementEvent('hint_requested', {
        quiz_id: quiz.quiz_id,
        question_id: currentQuestion.id,
        hint_type: hintData.hint_type || 'general'
      });
      
    } catch (error) {
      console.error('Failed to get hint:', error);
      setHint('Sorry, I couldn\'t generate a hint right now. Try thinking about the key concepts from the lesson.');
      setShowHint(true);
    }
  };

  const handleSubmitQuiz = async () => {
    if (!quiz) return;
    
    try {
      setLoading(true);
      
      const quizResults = await quizService.submitQuiz(
        quiz.quiz_id,
        answers,
        timeSpent,
        {
          questions_attempted: Object.keys(answers).length,
          hints_used: showHint ? 1 : 0,
          time_per_question: timeSpent / quiz.questions.length
        }
      );
      
      setResults(quizResults);
      
      // Track quiz completion
      await analyticsService.trackQuizCompleted(
        quiz.quiz_id,
        quizResults.overall_score,
        timeSpent
      );
      
      if (onQuizComplete) {
        onQuizComplete(quizResults);
      }
      
    } catch (error) {
      console.error('Failed to submit quiz:', error);
      setError('Failed to submit quiz. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const isQuizComplete = quiz && Object.keys(answers).length === quiz.questions.length;

  if (loading && !quiz) {
    return (
      <div className="quiz-interface loading">
        <div className="loading-spinner"></div>
        <p>Generating your personalized quiz...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="quiz-interface error">
        <div className="error-message">
          <h3>Oops! Something went wrong</h3>
          <p>{error}</p>
          <button onClick={generateQuiz} className="retry-button">
            Try Again
          </button>
          {onClose && (
            <button onClick={onClose} className="close-button">
              Close
            </button>
          )}
        </div>
      </div>
    );
  }

  if (results) {
    return (
      <QuizResults 
        results={results} 
        quiz={quiz!}
        onRetakeQuiz={() => {
          setResults(null);
          setAnswers({});
          setCurrentQuestionIndex(0);
          generateQuiz();
        }}
        onClose={onClose}
      />
    );
  }

  if (!quiz) {
    return null;
  }

  const currentQuestion = quiz.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / quiz.questions.length) * 100;

  return (
    <div className="quiz-interface">
      <div className="quiz-header">
        <div className="quiz-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <span className="progress-text">
            Question {currentQuestionIndex + 1} of {quiz.questions.length}
          </span>
        </div>
        
        <div className="quiz-info">
          <span className="time-spent">Time: {formatTime(timeSpent)}</span>
          <span className="difficulty">Difficulty: {quiz.difficulty_level}</span>
        </div>
        
        {onClose && (
          <button onClick={onClose} className="close-quiz-button">
            ✕
          </button>
        )}
      </div>

      <div className="quiz-content">
        <div className="question-container">
          <h3 className="question-text">{currentQuestion.question}</h3>
          
          <div className="answer-options">
            <div className="multiple-choice">
              {currentQuestion.options.map((option, index) => (
                <label key={index} className="option-label">
                  <input
                    type="radio"
                    name={currentQuestion.id}
                    value={option}
                    checked={answers[currentQuestion.id] === option}
                    onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                  />
                  <span className="option-text">{option}</span>
                </label>
              ))}
            </div>
          </div>

          {showHint && hint && (
            <div className="hint-container">
              <div className="hint-icon">💡</div>
              <div className="hint-text">{hint}</div>
            </div>
          )}
        </div>

        <div className="quiz-actions">
          <div className="navigation-buttons">
            <button
              onClick={handlePreviousQuestion}
              disabled={currentQuestionIndex === 0}
              className="nav-button prev-button"
            >
              ← Previous
            </button>
            
            <button
              onClick={handleGetHint}
              className="hint-button"
              disabled={showHint}
            >
              💡 Get Hint
            </button>
            
            {currentQuestionIndex < quiz.questions.length - 1 ? (
              <button
                onClick={handleNextQuestion}
                className="nav-button next-button"
              >
                Next →
              </button>
            ) : (
              <button
                onClick={handleSubmitQuiz}
                disabled={!isQuizComplete || loading}
                className="submit-button"
              >
                {loading ? 'Submitting...' : 'Submit Quiz'}
              </button>
            )}
          </div>
          
          <div className="quiz-status">
            <span className="answered-count">
              Answered: {Object.keys(answers).length} / {quiz.questions.length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizInterface;
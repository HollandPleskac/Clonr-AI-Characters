'use client';

import axios from 'axios';

export default function useSignups() {
    const signupPlus = async (): Promise<string> => {
        try {
          const response = await axios.post(
            `http://localhost:8000/signup/plus`,
            {
              withCredentials: true
            }
          );

          return response.data.id;
        } catch (error) {
          throw new Error('Error signing up for plus: ' + error.message);
        }
      };
    
    const signupCreators = async (): Promise<string> => {
        try {
          const response = await axios.post(
            `http://localhost:8000/signup/creators`,
            {
              withCredentials: true
            }
          );

          return response.data.id;
        } catch (error) {
          throw new Error('Error signing up for plus: ' + error.message);
        }
      };
    
      return {
        signupPlus,
        signupCreators,
      };
};
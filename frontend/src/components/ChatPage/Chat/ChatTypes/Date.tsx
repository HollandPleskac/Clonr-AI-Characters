import React from 'react';

interface DateProps {
  date: string;
}

const Date: React.FC<DateProps> = ({ date }) => {
  return (
    <div className='flex w-full justify-center text-[12px] font-light leading-4 text-[#979797] '>
      {date}
    </div>
  );
};

export default Date;

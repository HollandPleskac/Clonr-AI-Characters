import React from 'react';
import Image from 'next/image';

interface MyComponentProps {
  isActive: boolean;
  username: string;
  onClick: (username: string) => void;
}
const CharacterSmall: React.FC<MyComponentProps> = ({
  isActive,
  username,
  onClick
}) => (
  <div
    onClick={() => onClick(username)}
    className={`flex cursor-pointer bg-[#121212] px-4 py-[10px] transition duration-100 ${
      isActive ? 'bg-[#181620]' : 'bg-[#121212]'
    }`}
  >
    <Image
      key={0}
      src='/dummy-char.png' // Change to your image path
      alt={`Character Profile Picture ${0 + 1}`} // Change to your alt text
      width={48}
      height={48}
      className=' min-w-[48px] rounded-full'
    />
  </div>
);

export default CharacterSmall;

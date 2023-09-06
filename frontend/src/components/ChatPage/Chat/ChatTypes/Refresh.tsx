
import React from 'react';

interface DateProps {
    currentIndex: number
    messagesLength: number
    handleLeftArrow: () => void
    handleRightArrow: () => void
    handleRefresh: () => void
    isFetchingRegenMessage: boolean
    pressedRefreshIcon: boolean
}

const Date: React.FC<DateProps> = ({ currentIndex, messagesLength, handleLeftArrow, handleRightArrow, handleRefresh, isFetchingRegenMessage, pressedRefreshIcon }) => {

    let leftArrowNumber;
    if (pressedRefreshIcon) {
        leftArrowNumber = messagesLength + 1
    } else {
        if (!isFetchingRegenMessage) {
            leftArrowNumber = currentIndex + 1
        } else {
            leftArrowNumber = currentIndex + 2
        }
    }

    return (
        <div className='flex items-center ml-2' >
            <button
                disabled={isFetchingRegenMessage}
                onClick={handleRefresh} >
                <svg width="12px" height="12px" viewBox="0 0 24.00 24.00" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="#ededed" transform="rotate(0)"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round" stroke="#edededCCCCCC" strokeWidth="0.144"></g><g id="SVGRepo_iconCarrier"> <path d="M21 3V8M21 8H16M21 8L18 5.29168C16.4077 3.86656 14.3051 3 12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21C16.2832 21 19.8675 18.008 20.777 14" stroke="#ededed" strokeWidth="2.304" strokeLinecap="round" strokeLinejoin="round"></path> </g></svg>
            </button>
            {(messagesLength > 1 || isFetchingRegenMessage) && (
                <div className="flex justify-between ml-1">

                    <div className="text-xs flex items-center justify-center gap-1 self-center visible">
                        <button
                            disabled={currentIndex === 0 || isFetchingRegenMessage}
                            onClick={handleLeftArrow}
                            className="dark:text-white disabled:text-gray-300 dark:disabled:text-gray-400">
                            <svg stroke="currentColor" fill="none" strokeWidth="1.5" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className="h-3 w-3" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><polyline points="15 18 9 12 15 6"></polyline>
                            </svg>
                        </button>
                        <span className="flex-grow flex-shrink-0 text-white">{leftArrowNumber} / {!isFetchingRegenMessage ? messagesLength : messagesLength + 1}</span>
                        <button
                            disabled={currentIndex === messagesLength - 1 || isFetchingRegenMessage}
                            onClick={handleRightArrow}
                            className="dark:text-white disabled:text-gray-300 dark:disabled:text-gray-400">
                            <svg stroke="currentColor" fill="none" strokeWidth="1.5" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className="h-3 w-3" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><polyline points="9 18 15 12 9 6"></polyline>
                            </svg>
                        </button>
                    </div>
                    <div className="text-gray-400 flex self-end lg:self-center justify-center mt-2 gap-2 md:gap-3 lg:gap-1 lg:absolute lg:top-0 lg:translate-x-full lg:right-0 lg:mt-0 lg:pl-2 visible">
                        <button className="p-1 rounded-md hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 disabled:dark:hover:text-gray-400"><svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z">
                        </path>
                        </svg>
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Date;

import React from 'react';
import { cn } from '../../lib/utils';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

export const Skeleton: React.FC<SkeletonProps> = ({ className, ...props }) => {
  return (
    <div
      className={cn('animate-skeleton rounded-lg bg-muted', className)}
      {...props}
    />
  );
};

export const PropertyCardSkeleton: React.FC = () => {
  return (
    <div className="card p-0 overflow-hidden">
      {/* Image skeleton */}
      <Skeleton className="h-48 w-full rounded-none rounded-t-xl" />
      
      <div className="p-6">
        {/* Title skeleton */}
        <Skeleton className="h-6 w-3/4 mb-3" />
        
        {/* Price skeleton */}
        <Skeleton className="h-8 w-1/2 mb-4" />
        
        {/* Stats skeleton */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <Skeleton className="h-4 w-full mb-1" />
            <Skeleton className="h-5 w-3/4" />
          </div>
          <div>
            <Skeleton className="h-4 w-full mb-1" />
            <Skeleton className="h-5 w-3/4" />
          </div>
        </div>
        
        {/* Address skeleton */}
        <Skeleton className="h-4 w-full mb-2" />
        <Skeleton className="h-4 w-2/3 mb-4" />
        
        {/* Button skeleton */}
        <Skeleton className="h-10 w-full" />
      </div>
    </div>
  );
};

export const HeaderSkeleton: React.FC = () => {
  return (
    <div className="card mb-8">
      <div className="p-8">
        {/* Title skeleton */}
        <Skeleton className="h-8 w-1/2 mx-auto mb-4" />
        
        {/* Results count skeleton */}
        <Skeleton className="h-4 w-1/4 mx-auto mb-6" />
        
        {/* Filter controls skeleton */}
        <div className="flex gap-2 justify-center flex-wrap">
          <Skeleton className="h-9 w-20" />
          <Skeleton className="h-9 w-24" />
          <Skeleton className="h-9 w-28" />
          <Skeleton className="h-9 w-22" />
        </div>
      </div>
    </div>
  );
};
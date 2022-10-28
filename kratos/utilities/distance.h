//    |  /           |
//    ' /   __| _` | __|  _ \   __|
//    . \  |   (   | |   (   |\__ `
//   _|\_\_|  \__,_|\__|\___/ ____/
//                   Multi-Physics
//
//  License:         BSD License
//                   license: HDF5Application/license.txt
//
//  Main author:     Máté Kelemen
//

#pragma once

// --- STL Includes ---
#include <cmath>


namespace Kratos {


namespace Detail {


template <class TValue>
class Distance
{
public:
    Distance() noexcept {}

    static Distance FromSquaredDistance(TValue SquaredDistance)
    {return Distance(SquaredDistance);}

    static Distance FromDistance(TValue distance)
    {return Distance(distance * distance);}

    #define KRATOS_DEFINE_WRAPPED_LOGICAL_OPERATION(OPERATOR)                  \
        friend bool operator OPERATOR (Distance Left, Distance Right) noexcept \
        {return Left.mValue OPERATOR Right.mValue;}

    KRATOS_DEFINE_WRAPPED_LOGICAL_OPERATION(==)

    KRATOS_DEFINE_WRAPPED_LOGICAL_OPERATION(!=)

    KRATOS_DEFINE_WRAPPED_LOGICAL_OPERATION(<)

    KRATOS_DEFINE_WRAPPED_LOGICAL_OPERATION(>)

    KRATOS_DEFINE_WRAPPED_LOGICAL_OPERATION(<=)

    KRATOS_DEFINE_WRAPPED_LOGICAL_OPERATION(>=)

    #undef KRATOS_DEFINE_WRAPPED_LOGICAL_OPERATION

    explicit operator TValue() const noexcept
    {return std::sqrt(mValue);}

private:
    Distance(TValue SquaredDistance) noexcept
        : mValue(SquaredDistance)
    {}

    TValue mValue;
}; // class Distance


} // namespace Detail


using Distance = Detail::Distance<double>;


} // namespace Kratos

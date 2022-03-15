#include <stdio.h>
#include "dllmain.h"
#include <math.h>

#define DLL_EXPORT __declspec(dllexport)

Point DLL_EXPORT RayCast(int s_x,int s_y, int angle, int dist, Point* coords, size_t size) {
    float x = s_x, y = s_y, dx = cos((float)angle * 3.141 /180), dy = sin((float)angle * 3.141 / 180);
    Point cur_p;
    for (int w = 0; w < dist; w++) {
        for (size_t i = 0; i < size; i++) {
            cur_p.x = coords[i].x; cur_p.y = coords[i].y;
            if (x > cur_p.x && x < cur_p.x + 40 && y > cur_p.y && y < cur_p.y + 40) {
                cur_p.x = x; cur_p.y = y;
                return cur_p;
            }
        }
        x += dx; y += dy;
    }
    cur_p.x = x; cur_p.y = y;
    return cur_p;
}


DLL_EXPORT BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{   
    
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:    
    {
        
    }break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}


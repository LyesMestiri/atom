#ifndef PARTICLE_H
#define PARTICLE_H

#include <stdio.h>
#include <string>
#include <string.h>
#include <iostream>
#include <math.h>
#include "run_control.h"
#include "particle_types.h"
#include "tensor.h"

#define GPU_PARTICLE

#ifndef __CUDACC__
struct double3 {
    double x, y, z;
};
#endif

typedef struct Field {
    double3 E, H;
} Field;

class Particle {

public:
    double x, y, z, pu, pv, pw, m, q_m, x1, y1, z1;
    particle_sorts sort;

#ifdef DEBUG_PLASMA
    int fortran_number;
#endif

    __host__ __device__ Particle() {}

    __host__ __device__ __forceinline__
    Particle(double x1, double y1, double z1, double u1, double v1, double w1, double m1, double q_m1) : x(x1), y(y1), z(z1), pu(u1), pv(v1), pw(w1), m(m1), q_m(q_m1) {}

    __host__ __device__
    ~Particle() {}

    __host__ __device__
    void ElectricMove(double3 E, double tau, double q_m, double *tau1, double *pu, double *pv, double *pw, double *ps) {

        *tau1 = q_m * tau * 0.5;

        *pu += *tau1 * E.x;
        *pv += *tau1 * E.y;
        *pw += *tau1 * E.z;
        *ps = (*tau1) * pow(((*pu) * (*pu) + (*pv) * (*pv) + (*pw) * (*pw)) * 1. + 1.0, -0.5);
    }

    __host__ __device__ void MagneticMove(double3 H, double ps, double *pu1, double *pv1, double *pw1) {
        double bx, by, bz, s1, s2, s3, s4, s5, s6, s, su, sv, sw;

        bx = ps * H.x;
        by = ps * H.y;
        bz = ps * H.z;
        su = pu + pv * bz - pw * by;
        sv = pv + pw * bx - pu * bz;
        sw = pw + pu * by - pv * bx;

        s1 = bx * bx;
        s2 = by * by;
        s3 = bz * bz;
        s4 = bx * by;
        s5 = by * bz;
        s6 = bz * bx;
        s = s1 + 1. + s2 + s3;

        *pu1 = ((s1 + 1.) * su + (s4 + bz) * sv + (s6 - by) * sw) / s;
        *pv1 = ((s4 - bz) * su + (s2 + 1.) * sv + (s5 + bx) * sw) / s;
        *pw1 = ((s6 + by) * su + (s5 - bx) * sv + (s3 + 1.) * sw) / s;
    }

    __host__ __device__ double3 mult(double t, double3 t3) {
        t3.x *= t;
        t3.y *= t;
        t3.z *= t;

        return t3;
    }

    __host__ __device__ void add(double3 sx3, double *pu, double *pv, double *pw, double pu1, double pv1, double pw1) {
        *pu = pu1 + sx3.x;
        *pv = pv1 + sx3.y;
        *pw = pw1 + sx3.z;
    }

    __host__ __device__ double impulse(double pu, double pv, double pw) {
        return pow(((pu * pu + pv * pv + pw * pw) + 1.0), -0.5);
    }

    __host__ __device__ void mult(double *u, double *v, double *w, double ps, double pu, double pv, double pw) {
        *u = ps * pu;
        *v = ps * pv;
        *w = ps * pw;
    }

    __host__ __device__ __forceinline__
    void Move(Field fd, double tau) {
        double tau1, u, v, w, ps;
        double pu1, pv1, pw1;
        double3 sx3;

        ElectricMove(fd.E, tau, q_m, &tau1, &pu, &pv, &pw, &ps);

        MagneticMove(fd.H, ps, &pu1, &pv1, &pw1);

        sx3 = mult(tau1, fd.E);

        add(sx3, &pu, &pv, &pw, pu1, pv1, pw1);

        ps = impulse(pu, pv, pw);

        mult(&u, &v, &w, ps, pu, pv, pw);

        x1 = x + tau * u;
        y1 = y + tau * v;
        z1 = z + tau * w;
    }

    __host__ __device__ __forceinline__
    double3 GetX() {
        double3 d3x;
        d3x.x = x;
        d3x.y = y;
        d3x.z = z;
        return d3x;
    }

    __host__ __device__ __forceinline__
    double3 GetX1() {
        double3 d3x;
        d3x.x = x1;
        d3x.y = y1;
        d3x.z = z1;
        return d3x;
    }

    __host__ __device__ __forceinline__
    void SetX(double3 x1) {
        x = x1.x;
        y = x1.y;
        z = x1.z;
    }

    __host__ __device__
    Particle &operator=(Particle const &src) {
        x = src.x;
        y = src.y;
        z = src.z;
        pu = src.pu;
        pv = src.pv;
        pw = src.pw;
        m = src.m;
        q_m = src.q_m;
        sort = src.sort;
        x1 = src.x1;
        y1 = src.y1;
        z1 = src.z1;

#ifdef DEBUG_PLASMA
        fortran_number = src.fortran_number;
#endif
        return (*this);
    }
};

#endif

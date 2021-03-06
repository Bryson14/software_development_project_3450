from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import BaseUser, Attendant, Host, ParkingSpot, ParkingSize, Location, Reservation
from django.db.models import Q
from .serializers import (
    BaseUserSerializer,
    BaseUserUpdateSerializer,
    AttendantSerializer,
    HostSerializer,
    ParkingSizeSerializer,
    ParkingSpotSerializer,
    ParkingSpotCreateSerializer,
    ParkingSizeSerializer,
    ReservationSerializer,
    ReservationCreateSerialzier,
    LocationSerializer,
    LocationCreateSerializer,
)
from .permissions import AuthenticatedPermission, HostPermission, AttendantPermission
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny


SAFE_METHODS = ['list', 'retrieve']


class RegisterUser(CreateAPIView):
    serializer_class = BaseUserSerializer
    permission_classes=[AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()


class BaseUserViewSet(viewsets.ViewSet):
    
    def list(self, request):
        queryset = BaseUser.objects.all()
        serializer = BaseUserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = BaseUser.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = BaseUserSerializer(user)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        serializer = BaseUserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


    @action(detail=False, permission_classes=[])   
    def me(self, request):
        if request.user.is_authenticated:
            serializer = BaseUserSerializer(request.user)
            is_host = self.request.user.is_host()
            is_attendant = self.request.user.is_attendant()
            response_dict = {
                "user": serializer.data,
                "host": is_host,
                "attendant": is_attendant,       
            }
            if is_host: 
                response_dict['host_data'] = HostSerializer(Host.objects.get(user=request.user)).data
            if is_attendant: 
                response_dict['attendant_data'] = AttendantSerializer(Attendant.objects.get(user=request.user)).data
            return Response(response_dict)
        else:
            return Response({"error": "not found"}, status=404)


class AttendantViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Attendant.objects.all()
        serializer = AttendantSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Attendant.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = AttendantSerializer(user)
        return Response(serializer.data)

    def post(self, request):
        host_pk = request.data.get('host_pk', None)
        if not host_pk: 
            return Response({'success': False, 'message': 'must provide host pk'})
        if request.user.is_host(): 
            return Response({'success': False, 'message': 'you are already a host'})

        if request.user.is_attendant():
            return Response({'success': False, 'message': 'you are already an attendant'})
        else: 
            try: 
                boss = Host.objects.get(pk=host_pk)
                attendant = Attendant.objects.create(user=request.user, boss=boss)
                serialized_data = AttendantSerializer(attendant).data
                return Response({'success': True, 'attendant': serialized_data})
            except Exception as e: 
                return Response({'success': False, 'message': 'could not create attendant', 'error': str(e)})
    
    @action(detail=False, permission_classes=[HostPermission])
    def myattendants(self, request):
        host = Host.objects.get(user=request.user)
        attendants = Attendant.objects.filter(boss=host)
        serializer = AttendantSerializer(attendants, many=True)
        # serializer = ViewAttendantSerializer(attendants)
        return Response(serializer.data)

    

class HostViewSet(viewsets.ViewSet):
    
    def list(self, request):
        queryset = Host.objects.all()
        serializer = HostSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Host.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = HostSerializer(user)
        return Response(serializer.data)

    def post(self, request):
        if request.user.is_attendant(): 
            return Response({'success': False, 'message': 'you are already an attendant'})

        if request.user.is_host():
            return Response({'success': False, 'message': 'you are already a host'})
        else: 
            try: 
                host = Host.objects.create(user=request.user)
                serialized_data = HostSerializer(host).data
                return Response({'success': True, 'host': serialized_data})
            except Exception as e: 
                return Response({'success': False, 'message': 'could not create host', 'error': str(e)})
    
    @action(detail=True, methods=['post'], permission_classes=[HostPermission])   
    def fire(self, request, pk):
        queryset = Attendant.objects.filter(boss__user__pk=request.user.pk)
        try: 
            attendant = queryset.get(pk=pk)
            attendant.delete()
            return Response({'success': True, 'message': 'you just fired \'em good'})
        except Exception:
            return Response({'succcess': False, 'message': 'this is not your employee'})


class ParkingSpotViewSet(viewsets.ViewSet):
    
    def get_permissions(self):
        self.permission_classes = (HostPermission,)
        if self.action in SAFE_METHODS:
            self.permission_classes = (AllowAny,)
        return super(ParkingSpotViewSet, self).get_permissions()

    def get_queryset(self):
        '''
        possible query parameters:
        - location (string -> contains in spot location fields)
        - size (int -> pk)
        '''
        user = self.request.user
        queryset = ParkingSpot.objects.all()
        params = self.request.query_params
        location = params.get('location')
        size = params.get('size')
        if location:
            locations = location.split(' ')
            contains_query = Q()
            for location in locations:
                if location != '' and len(location) > 3:
                    contains_query |= (Q(location__name__icontains=location) |
                    Q(location__description__icontains=location) |
                    Q(location__address__icontains=location) |
                    Q(location__state__icontains=location) |
                    Q(location__city__icontains=location))
            queryset = queryset.filter(contains_query)
        if size and str.isdigit(size):
            queryset = queryset.filter(parking_size__pk=size)
        return queryset

    def list(self, request):
        serializer = ParkingSpotSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ParkingSpotSerializer(user)
        return Response(serializer.data)
        
    def post(self, request, pk=None, *args, **kwargs):
        if pk is None:
            request.data['owner'] = Host.objects.get(user__pk=request.user.pk).pk
            serializer = ParkingSpotCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else: 
            request.data['owner'] = request.user.pk
            instance = self.get_queryset().get(pk=pk)
            serializer = ParkingSpotCreateSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)

    @action(detail=False, permission_classes=[HostPermission])   
    def myspots(self, request): 
        queryset = ParkingSpot.objects.filter(owner__user__pk=request.user.pk)
        serializer = ParkingSpotSerializer(queryset, many=True)
        return Response(serializer.data)


class LocationViewSet(viewsets.ViewSet):

    def get_permissions(self):
        self.permission_classes = (HostPermission,)
        if self.action in SAFE_METHODS:
            self.permission_classes = (AllowAny,)
        return super(LocationViewSet, self).get_permissions()

    def get_queryset(self):
        queryset = Location.objects.all()
        if self.action not in SAFE_METHODS:
            queryset = queryset.filter(host__user__pk=self.request.user.pk)
        return queryset

    def list(self, request):
        serializer = LocationSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = LocationSerializer(user)
        return Response(serializer.data)
        
    def post(self, request, pk=None, *args, **kwargs):
        request.data['host'] = Host.objects.get(user__pk=request.user.pk).pk
        if pk is None:
            serializer = LocationCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else: 
            instance = self.get_queryset().get(pk=pk)
            serializer = LocationCreateSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)

    @action(detail=False, permission_classes=[])   
    def mylocations(self, request): 
        queryset = Location.objects.filter(host__user__pk=request.user.pk)
        serializer = LocationSerializer(queryset, many=True)
        return Response(serializer.data)


class ParkingSizeViewSet(viewsets.ViewSet):
    
    def get_queryset(self):
        return ParkingSize.objects.all()

    def get_permissions(self):
        self.permission_classes = (HostPermission,)
        if self.action in SAFE_METHODS:
            self.permission_classes = (AllowAny,)
        return super(ParkingSizeViewSet, self).get_permissions()

    def list(self, request):
        serializer = ParkingSizeSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ParkingSizeSerializer(user)
        return Response(serializer.data)
        
    def post(self, request, pk=None, *args, **kwargs):
        if pk: 
            instance = self.get_queryset().get(pk=pk)
            serializer = ParkingSizeSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = ParkingSizeSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)


class ReservationViewSet(viewsets.ViewSet):

    def get_queryset(self):
        queryset = Reservation.objects.all()
        user = self.request.user
        if self.action != 'retrieve':
            queryset = queryset.filter(canceled=False)
        if self.action in ['myreservations', 'confirm', 'cancel'] and user.is_host():
            queryset = queryset.filter(parking_spot__owner=Host.objects.get(user=user))
        elif self.action in ['bossreservations', 'confirm', 'cancel'] and user.is_attendant():
            attendant = Attendant.objects.get(user=user)
            if attendant.boss:
                queryset = queryset.filter(parking_spot__owner=Attendant.objects.get(user=user).boss)
            else:
                queryset = []
        else:
            queryset = queryset.filter(user=user)
        return queryset


    def list(self, request):
        serializer = ReservationSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ReservationSerializer(user)
        return Response(serializer.data)
        
    def post(self, request, pk=None, *args, **kwargs):
        request.data['user'] = request.user.pk
        if pk is None:
            serializer = ReservationCreateSerialzier(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            instance = self.get_queryset().get(pk=pk)
            serializer = ReservationSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)

    @action(detail=False, permission_classes=[HostPermission])
    def myreservations(self, request):
        serializer = ReservationSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, permission_classes=[AttendantPermission])
    def bossreservations(self, request):
        serializer = ReservationSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[AuthenticatedPermission])
    def cancel(self, request, pk=None):
        reservation = None
        if pk:
            reservation = user = get_object_or_404(Reservation, pk=pk)
            if reservation.canceled == True:
                return Response({'success': True, 'message': 'you have already canceled this reservation'})
            reservation.canceled = True
            reservation.save()
            return Response({'success': True, 'message': 'you have canceled reservation number: {}'.format(pk)})
        return Response({'success': False, 'message': 'you must specify a pk'})

    @action(detail=False, methods=['get'], permission_classes=[AttendantPermission])
    def needsconfirmation(self, request):
        is_attendant = request.user.is_attendant()
        is_host = request.user.is_host()
        queryset = []
        if is_host: 
            host = Host.objects.get(user__pk=request.user.pk)
            queryset = Reservation.objects.filter(parking_spot__owner__pk=host.pk, confirmed=False, canceled=False)
        if is_attendant:
            host = Attendant.objects.get(user__pk=request.user.pk).boss
            queryset = Reservation.objects.filter(parking_spot__owner__pk=host.pk, confirmed=False, canceled=False)
        serializer = ReservationSerializer(queryset, many=True)

        return Response(serializer.data)
        

    @action(detail=True, methods=['post'], permission_classes=[AttendantPermission])
    def confirm(self, request, pk=None):
        reservation = None
        if pk:
            reservation = user = get_object_or_404(Reservation, pk=pk)
            if reservation.confirmed == True:
                return Response({'success': True, 'message': 'you have already confirmed this reservation'})
            reservation.confirmed = True
            reservation.save()
            return Response({'success': True, 'message': 'you have confirmed reservation number: {}'.format(pk)})
        return Response({'success': False, 'message': 'you must specify a pk'})


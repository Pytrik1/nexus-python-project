close all
clc
clear

N=4;
time = [0 300];

%starting points for each agent 1 through 3
p01 = [5; 10];
p02 = [5; 12];
p03 = [2; 10];
p04 = [2; 12];

p0cen = 1/N*(p01+p02+p03+p04)
gamma0 = [0;0];
eta0 = [0; 0; 0; 0; 0; 0; 0; 0];
p0 = [p01; p02; p03; p04; gamma0; eta0];

%pbstacles
obs1 = [4; 7];
obs2 = [1; 4];
%Safe distance and Obstacle radii
Rsafe = 0.5;
Robs = 0.75;

%ode solver
tic
%for iteration = 1:1000
[t, p]=ode23(@formation,time,p0);
%end
toc;
%plotting
figure
hold on
plot(p01(1),p01(2), 'bo',...
     p02(1),p02(2), 'ro',...
     p03(1),p03(2), 'go',...
     p04(1),p04(2), 'mo',...
     p0cen(1),p0cen(2), 'black*',...
     p(:,1),p(:,2), 'b',...
     p(:,3),p(:,4), 'r',...
     p(:,5),p(:,6), 'g',...
     p(:,7),p(:,8), 'm',...
     (p(end,1)+p(end,3)+p(end,5)+p(end,7))/N,(p(end,2)+p(end,4)+p(end,6)+p(end,8))/N, 'black*',...
     [p01(1) p02(1)], [p01(2) p02(2)], 'black',...
     [p02(1) p03(1)], [p02(2) p03(2)], 'black',...
     [p03(1) p04(1)], [p03(2) p04(2)], 'black',...
     [p01(1) p03(1)], [p01(2) p03(2)], 'black',...
     [p01(1) p04(1)], [p01(2) p04(2)], 'black',...
     [p02(1) p04(1)], [p02(2) p04(2)], 'black',...
     [p(end,1) p(end,3)], [p(end,2) p(end,4)], 'black',...
     [p(end,1) p(end,5)], [p(end,2) p(end,6)], 'black',...
     [p(end,3) p(end,5)], [p(end,4) p(end,6)], 'black',...
     [p(end,1) p(end,7)], [p(end,2) p(end,8)], 'black',...
     [p(end,3) p(end,7)], [p(end,4) p(end,8)], 'black',...
     [p(end,5) p(end,7)], [p(end,6) p(end,8)], 'black');
circle(obs1(1),obs1(2),Robs+Rsafe,'b');
circle(obs1(1),obs1(2),Robs,'r');
circle(obs2(1),obs2(2),Robs+Rsafe,'b');
circle(obs2(1),obs2(2),Robs,'r');

axis([-2 13 -2 13]);
axis equal
xlabel('x')
ylabel('y')
legend('agent1', 'agent2', 'agent3', 'agent4')



function dx=formation(t,x)
    %Obstacles
    obs1 = [4; 7];
    obs2 = [1; 4];
    
    goal = [0; 0];
    
    %Safe distance and Obstacle radii
    Rsafe = 0.5;
    Robs = 0.75;

    %Gains
    cf = 10;
    cP = 1;
    cI = 0.9;
    calpha = 400;
    czeta = 10;
    
    %Desired relative distances
    p21_star = [0; 3];
    p31_star = [-2; 0];
    p41_star = [-2; 3];
 
    p01 = x([1 2]);
    p02 = x([3 4]);
    p03 = x([5 6]);
    p04 = x([7 8]);
    
    u1f = ((p02-p01)-p21_star+(p03-p01-(p31_star))+(p04-p01-(p41_star)));
    u2f = (((p01-p02)-(-p21_star))+(p03-p02-(p31_star-p21_star))+(p04-p02-(p41_star-p21_star)));
    u3f = ((p01-p03)-(-p31_star)+(p02-p03-(p21_star-p31_star))+(p04-p03-(p41_star-p31_star)));
    u4f = ((p01-p04-(-p41_star))+(p02-p04-(p21_star-p41_star))+(p03-p04-(p31_star-p41_star)));
    
    
    Uf = cf*[u1f; u2f; u3f; u4f]; 
    
    pcen = (1/3)*(p01+p02+p03+p04);
    gamma = x([9 10]);
    
    u1g = pcen-cI*gamma;
    u2g = pcen-cI*gamma;
    u3g = pcen-cI*gamma;
    u4g = pcen-cI*gamma;
    
    Ug = cP*[u1g; u2g; u3g; u4g];
    
    
    %Euclidian distances from each agent to each obstacle
%     p1_1 = abs(sqrt( (p01(1)-Obs1(1))^2 + (p01(2)-Obs1(2))^2) )-Robs-Rsafe;
%     p1_2 = abs(sqrt( (p01(1)-Obs2(1))^2 + (p01(2)-Obs2(2))^2) )-Robs-Rsafe;
%     
%     p2_1 = abs(sqrt( (p02(1)-Obs1(1))^2 + (p02(2)-Obs1(2))^2) )-Robs-Rsafe; 
%     p2_2 = abs(sqrt( (p02(1)-Obs2(1))^2 + (p02(2)-Obs2(2))^2) )-Robs-Rsafe;
%     
%     p3_1 = abs(sqrt( (p03(1)-Obs1(1))^2 + (p03(2)-Obs1(2))^2) )-Robs-Rsafe;
%     p3_2 = abs(sqrt( (p03(1)-Obs2(1))^2 + (p03(2)-Obs2(2))^2) )-Robs-Rsafe;
    
    %Angles between ech agent and each obstacle
%     phi1_1 = atan((Obs1(2)-p01(2))/(Obs1(1)-p01(1)));
%     phi1_2 = atan((Obs2(2)-p01(2))/(Obs2(1)-p01(1)));
%     
%     phi2_1 = atan((Obs1(2)-p02(2))/(Obs1(1)-p02(1)));
%     phi2_2 = atan((Obs2(2)-p02(2))/(Obs1(1)-p02(1)));
%     
%     phi3_1 = atan((Obs1(2)-p03(2))/(Obs1(1)-p03(1)));
%     phi3_2 = atan((Obs2(2)-p03(2))/(Obs2(1)-p03(1)));
    
    %Unit vector * gain
    alpha1_1 = (p01-obs1)/(norm(p01-obs1)) * 1/(norm(p01-obs1)-Robs);
    alpha1_2 = (p01-obs2)/(norm(p01-obs2)) * 1/(norm(p01-obs2)-Robs);
    
    alpha2_1 = (p02-obs1)/(norm(p02-obs1)) * 1/(norm(p02-obs1)-Robs);
    alpha2_2 = (p02-obs2)/(norm(p02-obs2)) * 1/(norm(p02-obs2)-Robs);
    
    alpha3_1 = (p03-obs1)/(norm(p03-obs1)) * 1/(norm(p03-obs1)-Robs);
    alpha3_2 = (p03-obs2)/(norm(p03-obs2)) * 1/(norm(p03-obs2)-Robs);
    
    alpha4_1 = (p04-obs1)/(norm(p04-obs1)) * 1/(norm(p04-obs1)-Robs);
    alpha4_2 = (p04-obs2)/(norm(p04-obs2)) * 1/(norm(p04-obs2)-Robs);
    
    agent_to_distance = [
        norm(p01-obs1)-Robs;
        norm(p01-obs2)-Robs;
        norm(p02-obs1)-Robs;
        norm(p02-obs2)-Robs;
        norm(p03-obs1)-Robs;
        norm(p03-obs2)-Robs;
        norm(p04-obs1)-Robs;
        norm(p04-obs2)-Robs];
    
    for i = 1:length(agent_to_distance)
        if agent_to_distance(i) <= Rsafe
            agent_to_distance(i) = 1;
        else
            agent_to_distance(i) = 0;
        end
    end
    
%     if sum(agent_to_distance) > 1
%         Uf = [0; 0; 0; 0; 0; 0; 0; 0];
%     end
    
    u1o = agent_to_distance(1)*calpha*alpha1_1 + agent_to_distance(2)*calpha*alpha1_2;
    u2o = agent_to_distance(3)*calpha*alpha2_1 + agent_to_distance(4)*calpha*alpha2_2;
    u3o = agent_to_distance(5)*calpha*alpha3_1 + agent_to_distance(6)*calpha*alpha3_2;
    u4o = agent_to_distance(7)*calpha*alpha4_1 + agent_to_distance(8)*calpha*alpha4_2;
    
    eta1 = x([11; 12]);
    eta2 = x([13; 14]);
    eta3 = x([15; 16]);
    eta4 = x([17; 18]);
    
    eta = [eta1; eta2; eta3; eta4]; 
    
    etadot1 = ((eta2-eta1)+(eta3-eta1)+(eta4-eta1))+u1o;
    etadot2 = ((eta1-eta2)+(eta3-eta2)+(eta4-eta2))+u2o;
    etadot3 = ((eta1-eta3)+(eta2-eta3)+(eta4-eta3))+u3o;
    etadot4 = ((eta1-eta4)+(eta2-eta4)+(eta3-eta4))+u4o;
    
    etaDot = czeta*[etadot1; etadot2; etadot3; etadot4];
    
    U0 = eta; 
    
    dx=[Uf-Ug+U0;-pcen+goal; etaDot];
        
    end




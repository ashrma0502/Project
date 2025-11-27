#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h> // Objective: Used to add timestamp at the time of allocation/deallocation
#include <stdbool.h> // Objective: Used to declare the boolean datatype as per need
// Objective: Structure used to store the student details
struct Student{
  int roll;
  char name[100];
  int seat_row;
  int seat_col;
};
// Objective: Structure used to store the seat on which a student is sitting
struct Seat{
  int rows,cols;
  int **seat;
};
int main(){
  struct Student **St=NULL;
  struct Seat Se;
  int students=0;
  char i='y';
  printf("Enter number of rows:");
  scanf(" %d",&Se.rows);
  printf("Enter number of columns:");
  scanf(" %d",&Se.cols);
  Se.seat=(int **)malloc(Se.rows*sizeof(int *));
  for(int r=0;r<Se.rows;r++){
    Se.seat[r]=(int *)calloc(Se.cols,sizeof(int));
  }
  FILE *fS=fopen("students.dat","rb");
  struct Student temp_St;
  if(fS!=NULL){
    while(fread(&temp_St,sizeof(struct Student),1,fS)==1){
    struct Student **temp_li=(struct Student **)realloc(St,(students+1)*sizeof(struct Student *));
    St=temp_li;
    St[students]=(struct Student *)malloc(sizeof(struct Student));
    memcpy(St[students],&temp_St,sizeof(struct Student));
    int r=temp_St.seat_row;
    int c=temp_St.seat_col;
    if(r>=0 && r<Se.rows && c>=0 && c<Se.cols){
      Se.seat[r][c]=temp_St.roll;
    }
    students++;
    }
    fclose(fS);
  }
  while(i=='y'){
    int t;
    printf("Main Menu:-\n1. Allocate Seat\n2. Deallocate Seat\n3. Display Hall\n4. Search Student\n5. View Log of Students\nEnter Task to be Performed (1-5):");
    scanf(" %d",&t);
    switch(t){
      // Objective: Perform the task of student allocation along with checking if a student is already allocated or not
      case 1:
      printf("Enter number of students to be allocated:");
      int n;
      scanf(" %d",&n);
      int rollA, rA, cA;
      char name[100];
      int allocated_count=0;
      for(int j=0;j<n;j++){
        bool empty_seat=false;
        rA=0;
        cA=0;
        for(int ro=0; ro<Se.rows;ro++){
          for(int co=0;co<Se.cols;co++){
            if(Se.seat[ro][co]==0){
              rA=ro;
              cA=co;
              empty_seat=true;
              break;
            }
          }
          if(empty_seat){
            break;
          }
        }
        if(!empty_seat){
          printf("\nHall is currently full. Allocated %d students before stopping.\n",allocated_count);
          break;
        }
        printf("--- Student %d/%d ---\n",j+1,n);
        printf("Roll Number: ");
        scanf(" %d", &rollA);
        printf("Name: ");
        scanf(" %s", name);
        bool duplicate=false;
        for(int k=0;k<students;k++){
          if(St[k] && St[k]->roll==rollA){
            printf("Error: Roll Number %d already allocated. Skipping this student.\n",rollA);
            duplicate=true;
            break;
          }
        }
        if(duplicate){
          continue;
        }
        struct Student **temp_li=(struct Student **)realloc(St,(students+1)*sizeof(struct Student *));
        St=temp_li;
        St[students]=(struct Student *)malloc(sizeof(struct Student));
        St[students]->roll=rollA;
        strcpy(St[students]->name,name);
        St[students]->seat_row=rA;
        St[students]->seat_col=cA;
        Se.seat[rA][cA]=rollA;
        FILE *fLA=fopen("allocation_log.txt","a");
        time_t now=time(NULL);
        struct tm *tinfo=localtime(&now);
        fprintf(fLA,"[%d-%d-%d %d:%d] Allocated seat (Row:%d,Column:%d) to Roll %d (%s)\n",tinfo->tm_mday,tinfo->tm_mon+1,tinfo->tm_year+1900,tinfo->tm_hour,tinfo->tm_min,rA+1,cA+1,rollA,name);
        fclose(fLA);
        students++;
        allocated_count++;
        printf("Seat allocated successfully at Row %d, Column %d.\n",rA+1,cA+1);
      }
      if(allocated_count>0){ 
        FILE *fSA=fopen("students.dat","wb"); 
        for(int j=0;j<students;j++){
          fwrite(St[j],sizeof(struct Student),1,fSA);
        }
        fclose(fSA);
      }
      if(n>0&&allocated_count==n){
        printf("%d Students Allocated successfully.\n",n);
      }
      break;
      // Objective: Perform the task of student deallocation along with checking if the student is present for deallocation or not
      case 2:
      printf("\nRoll Number to deallocate:");
      int rollD;
      scanf(" %d",&rollD);
      int found_position=-1;
      for(int i=0;i<students;i++){
        if(St[i] && St[i]->roll==rollD){
          found_position=i;
          break;
        }
      }
      if(found_position==-1){
        printf("Deallocation failed: Roll number %d not found.\n",rollD);
        break;
      }
      int r=St[found_position]->seat_row;
      int c=St[found_position]->seat_col;
      char student_name[100];
      strcpy(student_name,St[found_position]->name);
      FILE *fLD=fopen("allocation_log.txt","a");
      time_t now=time(NULL);
      struct tm *tinfo=localtime(&now);
      fprintf(fLD,"[%d-%d-%d %d:%d] Deallocated seat (Row:%d,Column:%d) of Roll %d (%s)\n",tinfo->tm_mday,tinfo->tm_mon+1,tinfo->tm_year+1900,tinfo->tm_hour, tinfo->tm_min,r+1,c+1,rollD,student_name);
      fclose(fLD);
      Se.seat[r][c]=0;
      free(St[found_position]);
      for(int i=found_position;i<students-1;i++){
        St[i]=St[i+1];
      }
      students--;
      if(students==0){
        free(St);
        St=NULL;
      }
      else{
        struct Student **temp_li=(struct Student **)realloc(St,students*sizeof(struct Student *));
        St=temp_li;
      }
      FILE *fSD_write=fopen("students.dat","wb");
      for(int j=0;j<students;j++){
        fwrite(St[j],sizeof(struct Student),1,fSD_write);
      }
      fclose(fSD_write);
      printf("Roll Number %d deallocated successfully from Row %d, Column %d.\n",rollD,r+1,c+1);
      break;
      // Objective: Performing the task of displaying the current hall layout
      case 3:
      printf("\nCurrent hall layout (0 means Empty seat):\n");
      for (int ro=0;ro<Se.rows;ro++){
        for (int co=0;co<Se.cols;co++){
          printf("%d\t",Se.seat[ro][co]);
        }
        printf("\n");
      }
      break;
      // Objective: Performing the task of searching the location of a student in the hall
      case 4:
      printf("Roll Number:");
      int rollS;
      scanf(" %d",&rollS);
      bool foundS=false;
      for(int i=0;i<students;i++){
        if(St[i] && St[i]->roll==rollS){
          printf("Student Found: %s\n",St[i]->name);
          printf("Assigned Seat: Row %d, Column %d\n",St[i]->seat_row+1,St[i]->seat_col+1);
          foundS=true;
          break;
        }
      }
      if(!foundS){
        printf("Student not found.\n");
      }
      break;
      // Objective: Display the complete list of students which have been allocated/deallocated by now along with their seat position and the time at which that task was performed
      case 5:
      printf("Log of students:\n");
      FILE *fSL=fopen("allocation_log.txt","r");
      if(fSL!=NULL) {
        char l[200];
        while((fgets(l,sizeof(l),fSL))!=NULL){
          printf("%s",l);
        }
        fclose(fSL);
      }
      else {
        printf("No log file found.\n");
      }
      break;
      default:
      printf("Invalid option\n");
      break;
    }
    // Objective: To ask the user if he/she wants to perform another task or not 
    // If y, then show the menu again and perform task as per the input
    // If n, then say thank you and program excution ends
    printf("\nWanna perform another task(y/n):");
    scanf(" %c",&i);
  }
  for(int r=0;r<Se.rows;r++){
    free(Se.seat[r]);
  }
  free(Se.seat);
  printf("Thank You");
  return 0;
}
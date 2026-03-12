package com.example.uetportal;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import java.util.ArrayList;
import java.util.List;

@Controller
public class HomeController {

    @GetMapping("/proposals")
    public String showProposals(Model model) {
        // This is our "mock" data, using YOUR exact project data
        List<Project> projectList = new ArrayList<>();
        projectList.add(new Project(1, "QWE", "QWE", 123.0, 123.0, "OPEN"));
        projectList.add(new Project(2, "jawad", "this is a project", 100000.0, 195000.0, "OPEN"));
        projectList.add(new Project(3, "Laptops", "Need some Laptops", 500000.0, 450000.0, "OPEN"));

        // Add the list of projects to the model so the HTML can see it
        model.addAttribute("projects", projectList);

        // Tell Spring to show the proposal.html page
        return "proposal";
    }
}